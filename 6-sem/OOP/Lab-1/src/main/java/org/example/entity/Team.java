package org.example.entity;

import lombok.AllArgsConstructor;
import lombok.Data;

import java.util.UUID;

@Data
@AllArgsConstructor
public class Team implements IId<UUID> {
    private UUID teamId;
    private UUID dispatcherId;
    private UUID workPlanId;

    public Team() {
        this.teamId = UUID.randomUUID();
        this.dispatcherId = null;
        this.workPlanId = null;
    }

    public UUID getId() {
        return teamId;
    }

    public void setId(UUID id) {
        this.teamId = id;
    }
}
