scoreboard players add #court_attempts alfheim.hub 1
execute in mythicbotany:alfheim as @e[type=minecraft:marker,tag=alfheim_hub_baked,tag=!alfheim_hub_buried,tag=!alfheim_court_refit_v2,limit=1] at @s positioned ~-.5 ~-1 ~5.5 run function alfheim:hub/court_refit/apply
execute if score #court_attempts alfheim.hub matches ..12 in mythicbotany:alfheim unless entity @e[type=minecraft:marker,tag=alfheim_court_refit_v2] run schedule function alfheim:hub/court_refit/poll 5s replace
