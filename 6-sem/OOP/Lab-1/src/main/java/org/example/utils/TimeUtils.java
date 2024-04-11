package org.example.utils;

import java.time.Duration;

public class TimeUtils {
    public static Duration pgIntervaltoDuration(org.postgresql.util.PGInterval interval) {
        return Duration.ofDays(interval.getDays())
                .plusHours(interval.getHours())
                .plusMinutes(interval.getMinutes())
                .plusSeconds((long) interval.getSeconds());
    }
}
