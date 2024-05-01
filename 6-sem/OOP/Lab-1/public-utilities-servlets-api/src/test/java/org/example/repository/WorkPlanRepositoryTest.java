package org.example.repository;

import org.example.dao.TeamDao;
import org.example.dao.WorkPlanDao;
import org.example.entity.WorkPlan;
import org.example.repository.impl.WorkPlanRepositoryImpl;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;

import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;

public class WorkPlanRepositoryTest {
    @Mock
    private WorkPlanDao workPlanDao;

    @Mock
    private TeamDao teamDao;

    @InjectMocks
    private WorkPlanRepositoryImpl workPlanRepository;

    @BeforeEach
    public void setup() {
        MockitoAnnotations.openMocks(this);
    }

    @Test
    public void testCreate() throws Exception {
        WorkPlan workPlan = new WorkPlan();
        workPlanRepository.create(workPlan);

        verify(workPlanDao, times(1)).create(workPlan);
    }

    @Test
    public void testRead() throws Exception {
        WorkPlan workPlan = new WorkPlan();

        workPlanRepository.read(workPlan.getWorkPlanId());

        verify(workPlanDao, times(1)).read(workPlan.getWorkPlanId());
    }
}
