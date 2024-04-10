package org.example.model;

import lombok.AllArgsConstructor;
import lombok.Data;

import java.util.UUID;

@Data
@AllArgsConstructor
public class Specialist implements IId<UUID>{
    private UUID id;
    private String name;
    private String specializtion;
    private UUID teamId;

    public Specialist() {
        this.id = UUID.randomUUID();
        this.name = "";
        this.specializtion = "";
        this.teamId = null;
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
