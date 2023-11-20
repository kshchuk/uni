package com.example.model;

import lombok.*;

import java.util.Objects;

@Getter
@Setter
@Builder
@ToString
@NoArgsConstructor
@AllArgsConstructor
public class Type {    
    private boolean peripheral;
    private int energyConsumption ;
    private boolean cooler;
    private String componentGroup;
    private String port;

    @Override
    public boolean equals(Object o) {
        if (this == o)
            return true;
        if (o == null || getClass() != o.getClass())
            return false;
        return hashCode() == o.hashCode();
    }

    @Override
    public int hashCode() {
        return Objects.hash(peripheral, energyConsumption, cooler, componentGroup, port);
    }
}
