package org.example;

import java.time.Duration;

public class Utils {
    public static String getRandString(int length) {
        var sb = new StringBuilder();
        for (int i = 0; i < length; i++) {
            sb.append((char) (Math.random() * 26 + 'a'));
        }
        return sb.toString();
    }

    public static Duration getRandDuration() {
        return Duration.ofHours((long) (Math.random() * 100));
    }

    public static Duration pgIntervaltoDuration(org.postgresql.util.PGInterval interval) {
        return Duration.ofDays(interval.getDays())
                .plusHours(interval.getHours())
                .plusMinutes(interval.getMinutes())
                .plusSeconds((long) interval.getSeconds());
    }
}
