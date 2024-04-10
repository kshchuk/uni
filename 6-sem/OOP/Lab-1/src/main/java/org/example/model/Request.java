package org.example.model;

import lombok.AllArgsConstructor;
import lombok.Data;

import java.time.Period;
import java.util.UUID;

@Data
@AllArgsConstructor
public class Request implements IId<UUID> {
    private UUID id;
    private UUID tenantId;
    private String workType;
    private String scopeOfWork;
    private Period desiredTime;

    public Request() {
        this.id = UUID.randomUUID();
        this.tenantId = null;
        this.workType = "";
        this.scopeOfWork = "";
        this.desiredTime = Period.ZERO;
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
