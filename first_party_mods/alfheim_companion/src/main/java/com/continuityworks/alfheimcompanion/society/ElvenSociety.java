package com.continuityworks.alfheimcompanion.society;

import com.continuityworks.alfheimcompanion.registry.ModEntities;
import com.continuityworks.alfheimcompanion.registry.ModItems;
import net.minecraft.world.item.ItemStack;

/** Stable role IDs are stored in NBT, independent of the model/skin catalogue order. */
public final class ElvenSociety {
    public static final String[] IDS={"serf","servant","steward","artisan","nobleman","noblewoman","lord","lady","prince","princess","king","queen"};
    public static final String[] NAMES={"Serf","Servant","Steward","Artisan","Nobleman","Noblewoman","Lord","Lady","Prince","Princess","King","Queen"};
    public static final String[] LOOKS={"Appearance I","Appearance II","Appearance III","Appearance IV"};
    public static String baseSkin(int role,int look){
        int variant=Math.floorMod(look,4);String name;
        if(gown(role))name="female_"+new int[]{1,2,3,1}[variant];
        else if(role>=4)name="male_"+new int[]{1,2,3,1}[variant];
        else name=new String[]{"male_1","female_1","male_3","female_3"}[variant];
        return "richs_races_wood_elves:entities/woodelf_"+name+"_texture";
    }
    public static int role(String id){for(int i=0;i<IDS.length;i++)if(IDS[i].equals(id))return i;return 0;}
    public static int safeRole(int role){return role>=0&&role<IDS.length?role:0;}
    public static boolean gown(int role){return role==5||role==7||role==9||role==11;}
    public static ItemStack selection(int role,int look) {
        var stack=new ItemStack(ModItems.ELVEN_CITIZEN_SPAWN_EGG.get());
        var tag=stack.getOrCreateTagElement("EntityTag");
        tag.putString("ElfRole",IDS[safeRole(role)]);tag.putInt("ElfAppearance",Math.floorMod(look,4));return stack;
    }
    public static int role(ItemStack stack){var tag=stack.getTagElement("EntityTag");return tag==null?0:role(tag.getString("ElfRole"));}
    public static int look(ItemStack stack){var tag=stack.getTagElement("EntityTag");return tag==null?0:Math.floorMod(tag.getInt("ElfAppearance"),4);}
    public static int modelKey(ItemStack stack){return role(stack)*4+look(stack)+1;}
    private ElvenSociety(){}
}
