package org.example.entity;

import lombok.AllArgsConstructor;
import lombok.Data;
import org.example.annotation.LazyLoad;

import java.util.List;
import java.util.UUID;

@Data
@AllArgsConstructor
public class Team implements IId<UUID> {
    private UUID teamId;
    private Specialist dispatcher;
    private WorkPlan workPlan;

    @LazyLoad
    private List<Specialist> specialists;

    public Team() {
        this.teamId = UUID.randomUUID();
        this.dispatcher = new Specialist();
        this.workPlan = new WorkPlan();
    }

    public UUID getId() {
        return teamId;
    }

    public void setId(UUID id) {
        this.teamId = id;
    }
}
