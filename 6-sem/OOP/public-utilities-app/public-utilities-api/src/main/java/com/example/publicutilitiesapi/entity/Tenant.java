package com.example.publicutilitiesapi.entity;

import jakarta.persistence.*;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import lombok.Getter;
import lombok.Setter;

import java.util.LinkedHashSet;
import java.util.Set;
import java.util.UUID;

@Getter
@Setter
@Entity
@Table(name = "tenant")
public class Tenant {
    @Id
    @Column(name = "tenant_id", nullable = false)
    private UUID id;

    @Size(max = 255)
    @NotNull
    @Column(name = "name", nullable = false)
    private String name;

    @Size(max = 255)
    @NotNull
    @Column(name = "address", nullable = false)
    private String address;

    @OneToMany(mappedBy = "tenant", fetch = FetchType.LAZY)
    private Set<Request> requests = new LinkedHashSet<>();

}