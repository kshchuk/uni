package org.example.dto;

import lombok.Data;

import java.util.List;

@Data
public class TenantDTO {
    private String tenantId;
    private String name;
    private String address;
    private List<String> requestIds;
}
