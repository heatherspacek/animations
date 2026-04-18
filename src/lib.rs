
use dat_tools::dat::{AnimationFrame, FighterData};

use glam::f32::{Mat4, Vec3};
use slp_parser::Character;

use core::panic;
use std::env;
use std::fs::File;
use std::io::{BufWriter, Write};

use pyo3::prelude::*;


#[pyfunction]
fn data_dump(iso_path: &str) -> PyResult<(
    Vec<Vec<String>>,  // Animations maps
    Vec<Vec<Vec<HurtBoxProcessed>>>, // Hurtbox lists
    Vec<Vec<Vec<HitBoxProcessed>>>, // Hitbox lists
)> {
    let file = std::fs::File::open(
        iso_path
    )?;
    let mut files = dat_tools::isoparser::ISODatFiles::new(file).unwrap();
    let all_characters = Character::AS_LIST;

    let mut all_animations_maps: Vec<Vec<String>> = Vec::new();
    let mut all_hitbox_lists: Vec<Vec<Vec<HitBoxProcessed>>> = Vec::new();
    let mut all_hurtbox_lists: Vec<Vec<Vec<HurtBoxProcessed>>> = Vec::new();

    for ch in all_characters {
        let character = ch.neutral();
        let data = dat_tools::get_fighter_data(&mut files, character).unwrap();
        if data.character_name.as_ref() == "Kirby" {
            continue;
        }

        all_animations_maps.push(get_anim_map(&data));
        // println!("DONE =========== {}", all_hitbox_lists.len());
        let (ch_hurts, ch_hits) = compute_frame_lists(
            &data, ch.to_u8_internal() as usize
        );
        all_hitbox_lists.push(ch_hits);
        all_hurtbox_lists.push(ch_hurts);
    }
    Ok((all_animations_maps, all_hurtbox_lists, all_hitbox_lists))
}


fn get_anim_map(fighter_data: &FighterData) -> Vec<String> {
    let mut char_ret: Vec<String> = Vec::new();
    for a in fighter_data.action_table.iter() {
        let name: &str = a.name.as_deref().map(dat_tools::dat::demangle_anim_name).flatten().unwrap_or("");
        char_ret.push(name.to_string());
    }
    char_ret
}

#[derive(Debug, Clone)]
struct HitboxDataFrame {
    frame: u32,
    hitbox_id: u8,
    bone_attachment: u8,
    damage: u16,
    x_offset: i16,
    y_offset: i16,
    z_offset: i16,
    size: u16,
    base_knockback: u16,
    knockback_growth: u16,
    knockback_angle: u16,
    set_knockback: u16,
}

#[pyclass]
struct HurtBoxProcessed {
    pos_a: Vec3,
    pos_b: Vec3,
    size: f32
}

#[pyclass]
struct HitBoxProcessed {
    frame_i: usize,
    hitbox_id: u8,
    damage: u16,
    knockback_angle: u16,
    base_knockback: u16,
    knockback_growth: u16,
    set_knockback: u16,
    pos: Vec3,
    size: f32,
}


static CHAR_SCALE_MAP: &[f32] = &[
    1.10, // Mario        
    0.96, // Fox          
    0.97, // CaptainFalcon
    1.00, // DonkeyKong   
    0.92, // Kirby        
    0.69, // Bowser       
    1.22, // Link         
    1.40, // Sheik        
    1.00, // Ness         
    1.15, // Peach        
    1.15, // Popo         
    1.15, // Nana         
    0.90, // Pikachu      
    0.88, // Samus        
    1.05, // Yoshi        
    0.94, // Jigglypuff   
    1.00, // Mewtwo       
    1.25, // Luigi        
    1.10, // Marth        
    1.26, // Zelda        
    0.96, // YoungLink    
    1.10, // DrMario      
    1.10, // Falco        
    0.50, // Pichu        
    1.02, // GameAndWatch 
    1.08, // Ganondorf    
    1.08, // Roy          
];

fn compute_frame_lists(fighter_data: &FighterData, fighter_internal_id: usize) -> 
    (Vec<Vec<HurtBoxProcessed>>, Vec<Vec<HitBoxProcessed>>)
{
    let mut fighter_hurt_lists: Vec<Vec<HurtBoxProcessed>> = Vec::new();
    let mut fighter_hit_lists: Vec<Vec<HitBoxProcessed>> = Vec::new();
    for action in fighter_data.action_table.iter().as_ref() {
        // ===== ONCE PER ACTION ... =====
        let mut action_hurt_list: Vec<HurtBoxProcessed> = Vec::new();
        let mut action_hit_list: Vec<HitBoxProcessed> = Vec::new();
        let (hits, clears) = hits_and_clears(
            action.subactions.as_ref()
        );
        let mut active_hb_slots: [Option<&HitboxDataFrame>; 16] = [None; 16];
        let mut anim: AnimationFrame = AnimationFrame::new_default_pose(&fighter_data.model);
        let mut world_transforms = vec![Mat4::IDENTITY; fighter_data.model.bones.len()];
        for (i, frame ) in action.animation.iter().enumerate() {
            // ===== ONCE PER FRAME ...
            anim.apply_animation(&fighter_data.model, frame, i as f32);
            
            for (bone_i, transform) in anim.transforms.iter().enumerate() {
                world_transforms[bone_i] = match fighter_data.model.bones[bone_i].parent {
                    Some(p_i) => world_transforms[p_i as usize] * *transform,
                    None => *transform
                };
            }

            // HURTbox math
            for hurtbox in fighter_data.hurtboxes.iter() {
                if hurtbox.bone >= world_transforms.len() as u8 {
                    // Kirby bullshit
                    continue;
                }
                let world_tform = world_transforms[hurtbox.bone as usize];
                
                let pos_a = world_tform.transform_point3(hurtbox.offset_1);
                let pos_b = world_tform.transform_point3(hurtbox.offset_2);
                let size = hurtbox.size * CHAR_SCALE_MAP[fighter_internal_id];

                action_hurt_list.push(HurtBoxProcessed { pos_a, pos_b, size })
            }
            // HITbox math
            // -> look for any `hitboxes` that just started; register em
            for this_hb in hits.iter() {
                if this_hb.frame == i as u32 {
                    active_hb_slots[this_hb.hitbox_id as usize] = Some(this_hb);
                }
            }
            //  if there is a clear on this frame:
            if clears.contains(&(i as usize)) {
                active_hb_slots.fill(Option::None);
            }

            for active_hitbox_maybe in active_hb_slots {
                if active_hitbox_maybe.is_none() { continue; }
                let this_hb = active_hitbox_maybe.unwrap();
                const SCALE: f32 = 0.003906;  // conversion to world units... lol
                let pt = Vec3::from([
                    this_hb.z_offset as f32,
                    this_hb.y_offset as f32,
                    this_hb.x_offset as f32,
                ])
                * SCALE
                * CHAR_SCALE_MAP[fighter_internal_id];
                let size = (this_hb.size as f32 * SCALE) * CHAR_SCALE_MAP[fighter_internal_id];
                let assoc_transform = world_transforms[(this_hb.bone_attachment) as usize];
                let resultant_pt: Vec3 = assoc_transform.transform_point3(pt);

                action_hit_list.push(HitBoxProcessed{
                    frame_i: i,
                    hitbox_id: this_hb.hitbox_id,
                    damage: this_hb.damage,
                    knockback_angle: this_hb.knockback_angle,
                    base_knockback: this_hb.base_knockback,
                    knockback_growth: this_hb.knockback_growth,
                    set_knockback: this_hb.set_knockback,
                    pos: resultant_pt,
                    size: size
                });
            }

        }

        fighter_hurt_lists.push(action_hurt_list);
        fighter_hit_lists.push(action_hit_list);
    }
    (fighter_hurt_lists, fighter_hit_lists)
}

fn hits_and_clears(subactions_list: Option<&Box<[u32]>>) ->
    (Vec<HitboxDataFrame>, Vec<usize>)
{
    let mut hits: Vec<HitboxDataFrame> = Vec::new();
    let mut clears: Vec<usize> = Vec::new();
    if let Some(subactions) = subactions_list.as_ref() {
        let mut f = 0;
        let mut i = 0;
        let mut subloop_start = 0usize;
        let mut subloop_i = 0usize;
        while i < subactions.len() {
            let word = subactions[i];
            let cmd = dat_tools::dat::subaction_cmd(word);
    
            use dat_tools::dat::Subaction as S;
            match dat_tools::dat::parse_next_subaction(&subactions[i..]) {
                S::EndOfScript => break,
                S::AsynchronousTimer { frame } => f = frame as usize,
                S::SynchronousTimer { frame } => f += frame as usize,

                S::SetLoop { loop_count } => {
                    subloop_start = i + dat_tools::dat::subaction_size(cmd);
                    subloop_i = loop_count as usize - 1;
                }
                S::ExecuteLoop if subloop_i != 0 => {
                    subloop_i -= 1;
                    i = subloop_start;

                    // skip index increment
                    continue;
                }
                
                S::CreateHitbox { hitbox_id,
                    bone_attachment,
                    damage,
                    x_offset,
                    y_offset,
                    z_offset,
                    size,
                    base_knockback,
                    knockback_growth,
                    knockback_angle,
                    weight_dependent_set_knockback,
                    .. } => {
                    hits.push(HitboxDataFrame {
                        frame: f as u32,
                        hitbox_id,
                        bone_attachment,
                        damage,
                        x_offset,
                        y_offset,
                        z_offset,
                        size,
                        base_knockback,
                        knockback_growth,
                        knockback_angle,
                        set_knockback: weight_dependent_set_knockback,
                    });
                },
                S::ClearHitboxes => {
                    // h_end = h_end.max(f as u32);
                    clears.push(f);
                },
                _ => (),
            }
            i += dat_tools::dat::subaction_size(cmd);
        }
    }
    (hits, clears)
}

// #[pyfunction]
// fn main() {
//     // input arguments: character, move id
//     let args: Vec<String> = env::args().collect();
//     let input_char = if args.len() < 3 { "fox" } 
//         else { args[1].as_str() };
//     let input_move: usize = if args.len() < 3 { 72 }
//         else { args[2].parse::<usize>().unwrap() };

//     let file_hurt = File::create("output_hurtboxes.crd").unwrap();
//     let file_hit = File::create("output_hitboxes.crd").unwrap();
//     let mut writer_hurt = BufWriter::new(file_hurt);
//     let mut writer_hit = BufWriter::new(file_hit);

//     let file = std::fs::File::open(
//         "/home/heather/Documents/Disk Images/Super Smash Bros. Melee (v1.02).iso"
//     ).unwrap();
//     let mut files = dat_tools::isoparser::ISODatFiles::new(file).unwrap();

//     let c = match input_char.to_lowercase().as_str() {
//         "fox" => Character::Fox,
//         "marth" => Character::Marth,
//         _ => panic!("Unknown character supplied (\"{}\")", args[1]),
//     };
    
//     let fi = dat_tools::get_fighter_data(&mut files, c.neutral()).unwrap();
//     let _hb = fi.hurtboxes.clone();
//     let _bones = fi.model.bones.clone();

//     let dash_attack = fi.action_table.get(input_move).unwrap().animation.clone().unwrap();
//     let _bone_trans = dash_attack.bone_transforms.clone(); // one for each bone!!!!!!!!!!
    
//     let mut anim: AnimationFrame = AnimationFrame::new_default_pose(&fi.model);

//     let mut hitboxes: Vec<HitboxDataFrame> = Vec::new();
//     let mut clears: Vec<usize> = Vec::new();
//     let mut h_end = 0u32;
//     if let Some(subactions) = fi.action_table[input_move].subactions.as_ref() {
//         let mut f = 0;
//         let mut i = 0;
//         let mut subloop_start = 0usize;
//         let mut subloop_i = 0usize;
//         while i < subactions.len() {
//             let word = subactions[i];
//             let cmd = dat_tools::dat::subaction_cmd(word);
    
//             use dat_tools::dat::Subaction as S;
//             match dat_tools::dat::parse_next_subaction(&subactions[i..]) {
//                 S::EndOfScript => break,
//                 S::AsynchronousTimer { frame } => f = frame as usize,
//                 S::SynchronousTimer { frame } => f += frame as usize,

//                 S::SetLoop { loop_count } => {
//                     subloop_start = i + dat_tools::dat::subaction_size(cmd);
//                     subloop_i = loop_count as usize - 1;
//                 }
//                 S::ExecuteLoop if subloop_i != 0 => {
//                     subloop_i -= 1;
//                     i = subloop_start;

//                     // skip index increment
//                     continue;
//                 }
                
//                 S::CreateHitbox { hitbox_id,
//                     bone_attachment,
//                     damage,
//                     x_offset,
//                     y_offset,
//                     z_offset,
//                     size,
//                     base_knockback,
//                     knockback_growth,
//                     knockback_angle,
//                     weight_dependent_set_knockback,
//                     .. } => {
//                     hitboxes.push(HitboxDataFrame {
//                         frame: f as u32,
//                         hitbox_id,
//                         bone_attachment,
//                         damage,
//                         x_offset,
//                         y_offset,
//                         z_offset,
//                         size,
//                         base_knockback,
//                         knockback_growth,
//                         knockback_angle,
//                         set_knockback: weight_dependent_set_knockback,
//                     });
//                 },
//                 S::ClearHitboxes => {
//                     h_end = h_end.max(f as u32);
//                     clears.push(f);
//                 },
//                 _ => (),
//             }
//             i += dat_tools::dat::subaction_size(cmd);
//         }

//         // println!("{:?}", hitboxes);
//         // println!("{:?}", clears);
//     }

//     let mut active_hb_slots: [Option<&HitboxDataFrame>; 16] = [None; 16];

//     let mut world_transforms =  vec![Mat4::IDENTITY; _bones.len()];
//     for frame_i in 0..(dash_attack.end_frame() as i32) {
//         let _ = writeln!(writer_hurt, "===");
//         let _ = writeln!(writer_hit, "===");
//         anim.apply_animation(&fi.model, &dash_attack, frame_i as f32);

//         // LATER: extracting model vertices -----------------------
//         // fi.model.vertices.iter()
//         //     .for_each(|x| println!("{},{},{}", x.pos().x, x.pos().y, x.pos().z));

//         // anim.transforms are LOCAL transforms.
//         //   "You can get a global transform by iterating 
//         //   "over the local transforms, and multiplying that local tform with the global 
//         //   "tform of it's parent, creating a new global tform for that idx."
        
//         for (bone_i, transform) in anim.transforms.iter().enumerate() {
//             world_transforms[bone_i] = match fi.model.bones[bone_i].parent {
//                 Some(p_i) => world_transforms[p_i as usize] * *transform,
//                 None => *transform
//             };
//         }

//         for i in 0.._hb.len() {
//             let hurtbox = &_hb[i];
//             // let parent_tform = match fi.model.bones[hurtbox.bone as usize].parent {
//             //     Some(p_i) => world_transforms[p_i as usize],
//             //     None => Mat4::IDENTITY
//             // };
//             let parent_tform = Mat4::IDENTITY;
//             let world_tform = world_transforms[hurtbox.bone as usize];
            
//             let pos_a = parent_tform.transform_point3(world_tform.transform_point3(hurtbox.offset_1));
//             let pos_b = parent_tform.transform_point3(world_tform.transform_point3(hurtbox.offset_2));
//             let size = hurtbox.size * CHAR_SCALE_MAP[c.to_u8_internal() as usize];
//             // println!("{},{},{},{},{},{},{}", pos_a.x, pos_a.y, pos_a.z, pos_b.x, pos_b.y, pos_b.z, size);
//             let _ = writeln!(
//                 writer_hurt,
//                 "{},{},{},{},{},{},{}",
//                 pos_a.x, pos_a.y, pos_a.z, pos_b.x, pos_b.y, pos_b.z, size
//             );
//         }
//         let _ = writer_hurt.flush();

//         // once per frame,
//         // -> look for any `hitboxes` that just started. register em
//         for this_hb in hitboxes.iter() {
//             if this_hb.frame == frame_i as u32 {
//                 active_hb_slots[this_hb.hitbox_id as usize] = Some(this_hb);
//             }
//         }
//         // if there is a clear on this frame:
//         if clears.contains(&(frame_i as usize)) {
//             active_hb_slots.fill(Option::None);
//         }

//         for active_hitbox_maybe in active_hb_slots {
//             if active_hitbox_maybe.is_none() { continue; }
//             let this_hb = active_hitbox_maybe.unwrap();
//             const SCALE: f32 = 0.003906;  // conversion to world units... lol
//             let pt = Vec3::from([
//                 this_hb.z_offset as f32,
//                 this_hb.y_offset as f32,
//                 this_hb.x_offset as f32,
//             ])
//             * SCALE
//             * CHAR_SCALE_MAP[c.to_u8_internal() as usize];
//             let connected_bone = this_hb.bone_attachment;
//             let assoc_transform = world_transforms[connected_bone as usize];
//             let resultant_pt: Vec3 = assoc_transform.transform_point3(pt);

//             let _ = writeln!(
//                 writer_hit,
//                 "{},{},{},{},{},{},{},{},{},{},{}",
//                 frame_i,
//                 this_hb.hitbox_id,
//                 this_hb.damage,
//                 this_hb.knockback_angle,
//                 this_hb.base_knockback,
//                 this_hb.knockback_growth,
//                 this_hb.set_knockback,
//                 resultant_pt.x,
//                 resultant_pt.y,
//                 resultant_pt.z,
//                 (this_hb.size as f32) * SCALE,
//             );
//         }
//     }

//     // println!("{} hurtboxes: {:?}", fi.hurtboxes.len(), fi.hurtboxes);  // 13, ASSOCIATED to bones.
//     // println!("{} bones: {:?}", bones.len(), bones);  // 73. Have "parents" and pgroup_start, pgroup_len
// }

#[pymodule]
mod animations {
    #[pymodule_export]
    use super::data_dump;
    #[pymodule_export]
    use super::HitBoxProcessed;
    #[pymodule_export]
    use super::HurtBoxProcessed;
}
