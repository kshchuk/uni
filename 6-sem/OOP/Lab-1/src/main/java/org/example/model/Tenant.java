package org.example.model;

import lombok.AllArgsConstructor;
import lombok.Data;

import java.util.UUID;

@Data
@AllArgsConstructor
public class Tenant implements IId<UUID>{
    private UUID id;
    private String name;
    private String address;

    public Tenant() {
        this.id = UUID.randomUUID();
        this.name = "";
        this.address = "";
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
