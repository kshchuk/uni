package org.example.entity;

import lombok.AllArgsConstructor;
import lombok.Data;

import java.time.Duration;
import java.util.UUID;

@Data
@AllArgsConstructor
public class WorkPlan {
    private UUID workPlanId;
    private String description;
    private Duration duration;
    private Team team;

    public WorkPlan() {
        this.workPlanId = UUID.randomUUID();
        this.description = "";
        this.team = null;
    }
}
