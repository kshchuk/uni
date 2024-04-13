package org.example.dto;

import lombok.Data;

import java.util.List;
import java.util.UUID;

@Data
public class TenantDTO {
    private UUID tenantId;
    private String name;
    private String address;
    private List<UUID> requestIds;
}
