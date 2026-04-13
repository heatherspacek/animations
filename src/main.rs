
use dat_tools::dat::AnimationFrame;
use dat_tools::dat::Model;
use dat_tools::dat::Hurtbox;

use glam::f32::{Quat, Mat4, Vec3};

fn hurtboxes() {
    let file = std::fs::File::open(
        "/home/heather/Documents/Disk Images/Super Smash Bros. Melee (v1.02).iso"
    ).unwrap();
    let mut files = dat_tools::isoparser::ISODatFiles::new(file).unwrap();

    let c = slp_parser::Character::Fox;
    let fi = dat_tools::get_fighter_data(&mut files, c.neutral()).unwrap();
    // let (mdl, anim) = dat_tools::get_common_model_and_animation(&mut files, 2);

    let _hb = fi.hurtboxes.clone();
    let _bones = fi.model.bones.clone();

    // println!("{:?}", fi.model.base_transforms.len()); // one for each bone.
    // println!("{:?}", fi.model.inv_world_transforms.len()); // one for each bone.

    let dash_attack = fi.action_table.get(052).unwrap().animation.clone().unwrap();
    let _bone_trans = dash_attack.bone_transforms.clone(); // one for each bone!!!!!!!!!!
    
    let mut anim: AnimationFrame = AnimationFrame::new_default_pose(&fi.model);

    // let mut world_transforms = fi.model.base_transforms.clone();
    let mut world_transforms =  vec![Mat4::IDENTITY; 73];
    for frame_i in 0..(dash_attack.end_frame() as i32) {
        // println!("FRAME #{} =====", frame_i);
        println!("===");
        anim.apply_animation(&fi.model, &dash_attack, frame_i as f32);

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
            // println!("=== hurtbox # {}", i);
            println!("{},{},{},{},{},{},{}", pos_a.x, pos_a.y, pos_a.z, pos_b.x, pos_b.y, pos_b.z, size);
        }

    }

    
    let _instructions: &str = "
    After you get an animation frame, each mat is a local transform for 
    the bone with the same index. You can get a global transform by iterating 
    over the local transforms, and multiplying that local tform with the global 
    tform of it's parent, creating a new global tform for that idx. The zero index 
    tform is the same. 
    
    Then multiply the two positions in a hurtbox capsule with it's 
    global tform to get the animated hurtbox.";

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


fn hitboxes() {
    let mut files = dat_tools::isoparser::ISODatFiles::new(file).unwrap();

    let c = slp_parser::Character::Fox;
    let fi = dat_tools::get_fighter_data(&mut files, c.neutral()).unwrap();

    let mut anim: AnimationFrame = AnimationFrame::new_default_pose(&fi.model);

    let dash_attack = fi.action_table.get(052).unwrap().animation.clone().unwrap();

    // let mut world_transforms = fi.model.base_transforms.clone();
    let mut world_transforms =  vec![Mat4::IDENTITY; 73];
    for frame_i in 0..(dash_attack.end_frame() as i32) {
        // println!("FRAME #{} =====", frame_i);
        println!("===");
        anim.apply_animation(&fi.model, &dash_attack, frame_i as f32);
    }
}


fn main() {
    // hurtboxes()
    hitboxes()
}