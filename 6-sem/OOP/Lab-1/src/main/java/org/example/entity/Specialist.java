package org.example.entity;

import lombok.AllArgsConstructor;
import lombok.Data;
import org.example.annotation.LazyLoad;

import java.util.List;
import java.util.UUID;

@Data
@AllArgsConstructor
public class Specialist implements IId<UUID>{
    private UUID specialistId;
    private String name;
    private String specializtion;
    private Team team;

    @LazyLoad
    private List<WorkPlan> workPlans;

    @LazyLoad
    private List<Request> requests;

    public Specialist() {
        this.specialistId = UUID.randomUUID();
        this.name = "";
        this.specializtion = "";
        this.team = null;
    }

    @Override
    public UUID getId() {
        return specialistId;
    }

    @Override
    public void setId(UUID id) {
        this.specialistId = id;
    }
}