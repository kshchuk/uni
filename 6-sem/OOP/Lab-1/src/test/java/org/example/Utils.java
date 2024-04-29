package org.example;

import org.example.entity.*;

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

    public static Request getRandomRequest(Tenant tenant) {
        var request = new Request();
        request.setTenant(tenant);
        request.setWorkType(getRandString(10));
        request.setScopeOfWork(getRandString(10));
        request.setDesiredTime(getRandDuration());

        return request;
    }

    public static Tenant getRandomTenant() {
        var tenant = new Tenant();
        tenant.setName(getRandString(10));
        tenant.setAddress(getRandString(10));

        return tenant;
    }

    public static Specialist getRandomSpecialist(Team team) {
        var specialist = new Specialist();
        specialist.setTeam(team);
        specialist.setName(getRandString(10));
        specialist.setSpecialization(getRandString(10));

        return specialist;
    }

    public static Team getRandomTeam(Specialist dispatcher) {
        var team = new Team();
        team.setDispatcher(dispatcher);

        return team;
    }

    public static WorkPlan getRandomWorkPlan(Team team) {
        var workPlan = new WorkPlan();
        workPlan.setTeam(team);
        workPlan.setDescription(getRandString(10));
        workPlan.setDuration(getRandDuration());

        return workPlan;
    }
}
