package org.example.entity;

import lombok.AllArgsConstructor;
import lombok.Data;

import java.util.List;
import java.util.UUID;

/// Class that represents a specialist in the system (dispatcher or worker)

@Data
@AllArgsConstructor
public class Specialist {
    private UUID specialistId;
    private String name;
    private String specialization;
    private Team team; // if the specialist is not a dispatcher

    private List<WorkPlan> workPlans;

    public Specialist() {
        this.specialistId = UUID.randomUUID();
        this.name = "";
        this.specialization = "";
        this.team = null;
    }
}
