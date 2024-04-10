package org.example.model;

import lombok.AllArgsConstructor;
import lombok.Data;

import java.util.UUID;

@Data
@AllArgsConstructor
public class Team implements IId<UUID> {
    private UUID id;
    private UUID dispatcherId;
    private UUID workPlanId;

    public Team() {
        this.id = UUID.randomUUID();
        this.dispatcherId = null;
        this.workPlanId = null;
    }

    @Override
    public UUID getId() {
        return id;
    }

    @Override
    public void setId(UUID id) {
        this.id = id;
    }
}
