package org.example.entity;

import lombok.AllArgsConstructor;
import lombok.Data;

import java.util.List;
import java.util.UUID;

@Data
@AllArgsConstructor
public class Team {
    private UUID teamId;
    private Specialist dispatcher;

    private List<Specialist> specialists;

    private List<WorkPlan> workPlans;

    public Team() {
        this.teamId = UUID.randomUUID();
        this.dispatcher = null;
    }
}
