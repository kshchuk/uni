package org.example.model;

import lombok.AllArgsConstructor;
import lombok.Data;

import java.util.UUID;

@Data
@AllArgsConstructor
public class WorkPlan implements IId<UUID> {
    private UUID id;
    private UUID teamId;
    private String description;

    public WorkPlan() {
        this.id = UUID.randomUUID();
        this.teamId = null;
        this.description = "";
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
