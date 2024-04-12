package org.example.entity;

import lombok.AllArgsConstructor;
import lombok.Data;

import java.time.Duration;
import java.util.UUID;

@Data
@AllArgsConstructor
public class Request implements IId<UUID> {
    private UUID requestId;
    private Tenant tenant;
    private String workType;
    private String scopeOfWork;
    private Duration desiredTime;

    public Request() {
        this.requestId = UUID.randomUUID();
        this.tenant = null;
        this.workType = "";
        this.scopeOfWork = "";
        this.desiredTime = Duration.ZERO;
    }

    @Override
    public UUID getId() {
        return requestId;
    }

    @Override
    public void setId(UUID id) {
        this.requestId = id;
    }
}
