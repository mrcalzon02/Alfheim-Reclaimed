package com.continuityworks.alfheimcompanion.command;

import java.util.Locale;
import java.util.Optional;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public final class AddressedCommandParser {
    public enum Verb { FOLLOW, GUARD, SHOW_ITEM, FETCH_ITEM, LEAD_TO_ITEM, CRAFT, BUILD, QUEST, CANCEL, STATUS }
    public record Parsed(Verb verb, String target, int count) {}

    private static final Pattern COUNT = Pattern.compile("^(\\d+)\\s+(.+)$");

    private AddressedCommandParser() {}

    public static Optional<Parsed> parse(String companionName, String rawMessage) {
        if (companionName == null || companionName.isBlank() || rawMessage == null) return Optional.empty();
        String message = rawMessage.strip();
        if (!message.regionMatches(true, 0, companionName, 0, companionName.length())) return Optional.empty();
        if (message.length() == companionName.length()) return Optional.empty();
        char boundary = message.charAt(companionName.length());
        if (!(Character.isWhitespace(boundary) || boundary == ',' || boundary == ':' || boundary == ';')) {
            return Optional.empty();
        }

        String body = message.substring(companionName.length()).replaceFirst("^[\\s,:;]+", "")
                .strip().toLowerCase(Locale.ROOT);
        if (body.equals("follow") || body.equals("follow me")) return parsed(Verb.FOLLOW, "", 1);
        if (body.equals("guard") || body.equals("guard here") || body.equals("stay here"))
            return parsed(Verb.GUARD, "", 1);
        if (body.equals("cancel") || body.equals("stop")) return parsed(Verb.CANCEL, "", 1);
        if (body.equals("status") || body.equals("what are you doing")) return parsed(Verb.STATUS, "", 1);

        Optional<Parsed> matched;
        matched = target(body, Verb.LEAD_TO_ITEM, "bring me to ", "lead me to ", "take me to ");
        if (matched.isPresent()) return matched;
        matched = target(body, Verb.FETCH_ITEM, "bring me ", "fetch ", "get me ", "go get ");
        if (matched.isPresent()) return matched;
        matched = target(body, Verb.SHOW_ITEM, "where is ", "show me ", "locate ", "find ");
        if (matched.isPresent()) return matched;
        matched = target(body, Verb.CRAFT, "help me craft ", "help me make ", "craft ", "make ");
        if (matched.isPresent()) return matched;
        matched = target(body, Verb.BUILD, "help me build ", "build ");
        if (matched.isPresent()) return matched;
        return target(body, Verb.QUEST, "quest ", "tell me about quest ", "what quest ");
    }

    private static Optional<Parsed> target(String body, Verb verb, String... prefixes) {
        for (String prefix : prefixes) {
            if (!body.startsWith(prefix) || body.length() <= prefix.length()) continue;
            String target = body.substring(prefix.length()).strip();
            int count = 1;
            Matcher matcher = COUNT.matcher(target);
            if (matcher.matches()) {
                try { count = Math.max(1, Math.min(64, Integer.parseInt(matcher.group(1)))); }
                catch (NumberFormatException ignored) {}
                target = matcher.group(2).strip();
            }
            if (!target.isBlank()) return parsed(verb, target, count);
        }
        return Optional.empty();
    }

    private static Optional<Parsed> parsed(Verb verb, String target, int count) {
        return Optional.of(new Parsed(verb, target, count));
    }
}
