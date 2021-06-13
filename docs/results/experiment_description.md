
|Algo   |Env   |Name   |description  |results  |
|---|---|---|---|---|
|MSAC   |Walker2DBulletEnv-v0   |Walker2DBulletEnv-v0_1_no_clipping   | M-SAC completely without clipping otherwise everything as originally.  | is worse than the implementation as in the paper|
|MSAC   |Walker2DBulletEnv-v0   |Walker2DBulletEnv-v0_1_no_clipping_fix_m-scale_0-03   | M-SAC completely without clipping and with a fixed scaling parameter. mscale+teprature=0.03   |is worse than the implementation as in the paper|
|MSAC   |HalfCheetahBulletEnv-v0   |HalfCheetahBulletEnv-v0_max_clipp_5    |The upper value of the clipping is set to 5   |Is worse than the original implementation. A clipping of 5 also makes no sense, since the values are on average at 0.2.| 
|MSAC   |HalfCheetahBulletEnv-v0   |HalfCheetahBulletEnv-v0_max_clipp_3   |The upper value of the clipping is set to 3   |Is worse than the original implementation. A clipping of 3 also makes no sense, since the values are on average at 0.2.|
|---|---|---|---|---|
|SAC   |HalfCheetahBulletEnv-v0   |HalfCheetahBulletEnv-v0_1_sac_entropy   |same as SAC/HalfCheetahBulletEnv-v0_1 but with entropy logged. The MSAC Algo was used with mscale=0.  |   | 
|MSAC   |HalfCheetahBulletEnv-v0   |HalfCheetahBulletEnv-v0_1_msac_entropy   |same as MSAC/HalfCheetahBulletEnv-v0_1 but with entropy logged.   |  | 
|MSAC   |HalfCheetahBulletEnv-v0   |HalfCheetahBulletEnv-v0_1_max_clipp_0-05   |The upper value of the clipping is set to 0.05   |   | 
|MSAC   |HalfCheetahBulletEnv-v0   |HalfCheetahBulletEnv-v0_1_max_clipp_100_min_clipp_0.4   |The upper value of the clipping is set to +100 the lower one to +0.4   |   | 