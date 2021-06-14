
|Algo   |Env   |Name   |description  |results  |
|---|---|---|---|---|
|MSAC   |Walker2DBulletEnv-v0   |Walker2DBulletEnv-v0_1_no_clipping   | M-SAC completely without clipping otherwise everything as originally.  | is worse than the implementation as in the paper|
|MSAC   |Walker2DBulletEnv-v0   |Walker2DBulletEnv-v0_1_no_clipping_fix_m-scale_0-03   | M-SAC completely without clipping and with a fixed scaling parameter. mscale+teprature=0.03   |is worse than the implementation as in the paper|
|MSAC   |HalfCheetahBulletEnv-v0   |HalfCheetahBulletEnv-v0_max_clipp_5    |The upper value of the clipping is set to 5   |Is worse than the original implementation. A clipping of 5 also makes no sense, since the values are on average at 0.2. Nose continuous on the ground  | 
|MSAC   |HalfCheetahBulletEnv-v0   |HalfCheetahBulletEnv-v0_max_clipp_3   |The upper value of the clipping is set to 3   |Is worse than the original implementation. A clipping of 3 also makes no sense, since the values are on average at 0.2. Dolphin movement|
|---|---|---|---|---|
|SAC   |HalfCheetahBulletEnv-v0   |HalfCheetahBulletEnv-v0_1_sac_entropy   |same as SAC/HalfCheetahBulletEnv-v0_1 but with entropy logged. The MSAC Algo was used with mscale=0.  | Dolphin movement  | 
|MSAC   |HalfCheetahBulletEnv-v0   |HalfCheetahBulletEnv-v0_1_msac_entropy   |same as MSAC/HalfCheetahBulletEnv-v0_1 but with entropy logged.   | Nose continuous on the ground  | 
|MSAC   |HalfCheetahBulletEnv-v0   |HalfCheetahBu   |The upper value of the clipping is set to +100 the lower one to +0.4   | Dolphin movement   | 
|---|---|---|---|---|
|SAC   |AntBulletEnv-v0   |AntBulletEnv-v0_1_sac_entropy   |same as SAC/AntBulletEnv-v0_1 but with entropy logged. |   | 
|MSAC   |AntBulletEnv-v0   |AntBulletEnv-v0_1_msac_entropy   |same as MSAC/AntBulletEnv-v0_1 but with entropy logged.   |  | 
|---|---|---|---|---|
|MSAC   |HalfCheetahBulletEnv-v0   |HalfCheetahBulletEnv-v0_1_shift_04   |shift the log_prob to the area [-1;0] `next_munchausen_values = ent_coef * (log_prob.reshape(-1, 1)) - 0.4`  | Running movement with little use of the front legs. Dolphin movement  | 
|MSAC   |HalfCheetahBulletEnv-v0   |HalfCheetahBulletEnv-v0_1_shift_30   |shift the log_prob to the area [-1;0] `ent_coef * (log_prob.reshape(-1, 1)-30.0)`  | Running movement without intensive use of the front legs.   | 


