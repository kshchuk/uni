package org.example.entity;

import lombok.AllArgsConstructor;
import lombok.Data;

import java.util.List;
import java.util.UUID;

@Data
@AllArgsConstructor
public class Tenant {
    private UUID tenantId;
    private String name;
    private String address;
    
    private List<Request> requests;

    public Tenant() {
        this.tenantId = UUID.randomUUID();
        this.name = "";
        this.address = "";
    }
}
