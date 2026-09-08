package com.continuityworks.alfheimcompanion.personality;

public record PersonalityProfile(String name, String temperament, String cadence, String coreValue,
                                 String humor, String favoriteTerrain, String favoriteFood,
                                 String favoriteColor, String favoriteActivity,
                                 String pathAdjective, String summonLine,
                                 String followLine, String waitLine, String acknowledgement) {
    public String promptSummary() {
        return "temperament=" + temperament + "; cadence=" + cadence + "; value=" + coreValue
                + "; humor=" + humor + "; favorites=" + favoriteTerrain + ", " + favoriteFood
                + ", " + favoriteColor + ", " + favoriteActivity
                + "; voice must remain concise and never override safety rules";
    }
}
