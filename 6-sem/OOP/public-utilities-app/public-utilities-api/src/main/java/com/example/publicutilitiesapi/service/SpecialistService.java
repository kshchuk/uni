package com.example.publicutilitiesapi.service;

import com.example.publicutilitiesapi.entity.Specialist;
import com.example.publicutilitiesapi.repository.SpecialistRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Service;

import java.util.UUID;

@Service
public class SpecialistService extends CrudService<Specialist, UUID> {

    private final SpecialistRepository specialistRepository;

    @Autowired
    public SpecialistService(SpecialistRepository specialistRepository) {
        this.specialistRepository = specialistRepository;
    }

    @Override
    protected JpaRepository<Specialist, UUID> getRepository() {
        return specialistRepository;
    }
}
