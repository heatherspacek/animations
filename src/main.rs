
use dat_tools::dat::AnimationFrame;

use glam::f32::{Mat4, Vec3};

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

fn main() {
    const MOVE_ID: usize = 072;

    let file = std::fs::File::open(
        "/home/heather/Documents/Disk Images/Super Smash Bros. Melee (v1.02).iso"
    ).unwrap();
    let mut files = dat_tools::isoparser::ISODatFiles::new(file).unwrap();

    let c = slp_parser::Character::Fox;
    let fi = dat_tools::get_fighter_data(&mut files, c.neutral()).unwrap();
    // let (mdl, anim) = dat_tools::get_common_model_and_animation(&mut files, 2);

    let _hb = fi.hurtboxes.clone();
    let _bones = fi.model.bones.clone();

    let dash_attack = fi.action_table.get(MOVE_ID).unwrap().animation.clone().unwrap();
    let _bone_trans = dash_attack.bone_transforms.clone(); // one for each bone!!!!!!!!!!
    
    let mut anim: AnimationFrame = AnimationFrame::new_default_pose(&fi.model);

    let mut hitboxes: Vec<HitboxDataFrame> = Vec::new();
    let mut clears: Vec<usize> = Vec::new();
    let mut h_end = 0u32;
    if let Some(subactions) = fi.action_table[MOVE_ID].subactions.as_ref() {
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
                    hitboxes.push(HitboxDataFrame {
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
                    h_end = h_end.max(f as u32);
                    clears.push(f);
                },
                _ => (),
            }
            i += dat_tools::dat::subaction_size(cmd);
        }

        println!("{:?}", hitboxes);
        println!("{:?}", clears);
    }

    let mut active_hb_slots: [Option<&HitboxDataFrame>; 16] = [None; 16];

    // let mut world_transforms = fi.model.base_transforms.clone();
    let mut world_transforms =  vec![Mat4::IDENTITY; 73];
    for frame_i in 0..(dash_attack.end_frame() as i32) {
        // println!("FRAME #{} =====", frame_i);
        println!("===");
        anim.apply_animation(&fi.model, &dash_attack, frame_i as f32);

        // LATER: extracting model vertices -----------------------
        // fi.model.vertices.iter()
        //     .for_each(|x| println!("{},{},{}", x.pos().x, x.pos().y, x.pos().z));

        // anim.transforms are LOCAL transforms.
        //   "You can get a global transform by iterating 
        //   "over the local transforms, and multiplying that local tform with the global 
        //   "tform of it's parent, creating a new global tform for that idx."
        
        for (bone_i, transform) in anim.transforms.iter().enumerate() {
            world_transforms[bone_i] = match fi.model.bones[bone_i].parent {
                Some(p_i) => world_transforms[p_i as usize] * *transform,
                None => *transform
            };
        }

        for i in 0.._hb.len() {
            let hurtbox = &_hb[i];
            // let parent_tform = match fi.model.bones[hurtbox.bone as usize].parent {
            //     Some(p_i) => world_transforms[p_i as usize],
            //     None => Mat4::IDENTITY
            // };
            let parent_tform = Mat4::IDENTITY;
            let world_tform = world_transforms[hurtbox.bone as usize];
            
            let pos_a = parent_tform.transform_point3(world_tform.transform_point3(hurtbox.offset_1));
            let pos_b = parent_tform.transform_point3(world_tform.transform_point3(hurtbox.offset_2));
            let size = hurtbox.size * 0.96;
            // println!("{},{},{},{},{},{},{}", pos_a.x, pos_a.y, pos_a.z, pos_b.x, pos_b.y, pos_b.z, size);
        }

        // once per frame,
        // -> look for any `hitboxes` that just started. register em
        for this_hb in hitboxes.iter() {
            if this_hb.frame == frame_i as u32 {
                active_hb_slots[this_hb.hitbox_id as usize] = Some(this_hb);
            }
        }
        // if there is a clear on this frame:
        if clears.contains(&(frame_i as usize)) {
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
            ]) * SCALE;
            let connected_bone = this_hb.bone_attachment;
            let assoc_transform = world_transforms[connected_bone as usize];
            let resultant_pt: Vec3 = assoc_transform.transform_point3(pt);

            println!(
                "{},{},{},{},{},{},{},{},{},{},{}",
                frame_i,
                this_hb.hitbox_id,
                this_hb.damage,
                this_hb.knockback_angle,
                this_hb.base_knockback,
                this_hb.knockback_growth,
                this_hb.set_knockback,
                resultant_pt.x,
                resultant_pt.y,
                resultant_pt.z,
                (this_hb.size as f32) * SCALE,
            )
        }
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

    // println!("{} hurtboxes: {:?}", fi.hurtboxes.len(), fi.hurtboxes);  // 13, ASSOCIATED to bones.
    // println!("{} bones: {:?}", bones.len(), bones);  // 73. Have "parents" and pgroup_start, pgroup_len
}
