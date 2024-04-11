package org.example.entity;

import lombok.AllArgsConstructor;
import lombok.Data;

import java.util.UUID;

@Data
@AllArgsConstructor
public class Tenant implements IId<UUID>{
    private UUID tenantId;
    private String name;
    private String address;

    public Tenant() {
        this.tenantId = UUID.randomUUID();
        this.name = "";
        this.address = "";
    }

    public UUID getId() {
        return tenantId;
    }

    public void setId(UUID id) {
        this.tenantId = id;
    }
}
