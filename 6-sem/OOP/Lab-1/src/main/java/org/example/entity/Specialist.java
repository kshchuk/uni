package org.example.entity;

import lombok.AllArgsConstructor;
import lombok.Data;

import java.util.UUID;

@Data
@AllArgsConstructor
public class Specialist implements IId<UUID>{
    private UUID specialistId;
    private String name;
    private String specializtion;
    private UUID teamId;

    public Specialist() {
        this.specialistId = UUID.randomUUID();
        this.name = "";
        this.specializtion = "";
        this.teamId = null;
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
