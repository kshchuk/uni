package org.example.dto;

import lombok.Data;

import java.util.List;
import java.util.UUID;

@Data
public class TenantDTO {
    private String tenantId;
    private String name;
    private String address;
    private List<String> requestIds;
}
