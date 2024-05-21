package com.example.publicutilitiesapi.controller;

import com.example.publicutilitiesapi.dto.WorkPlanDto;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/work-plan/")
public class WorkPlanController {
    @GetMapping("/all")
    public List<WorkPlanDto> getAllWorkPlans() {
        /// TODO: Implement this method
        return null;
    }
}
