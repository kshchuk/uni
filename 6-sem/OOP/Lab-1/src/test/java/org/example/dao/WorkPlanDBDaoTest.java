package org.example.dao;

import org.example.dao.db.DAOManager;
import org.example.entity.WorkPlan;
import org.junit.jupiter.api.*;

import static org.example.Utils.getRandDuration;
import static org.example.Utils.getRandString;
import static org.junit.jupiter.api.Assertions.*;

public class WorkPlanDBDaoTest {
    private WorkPlanDao workPlanDBDao;
    private int dataBaseSize;

    @BeforeEach
    public void setUp() throws Exception {
        var manager = DAOManager.getInstance();
        workPlanDBDao = (WorkPlanDao) manager.getDAO(DAOManager.Table.WORKPLAN);
        dataBaseSize = workPlanDBDao.findAll().size();
    }

    @Test
    public void testCreate() throws Exception {
        var workPlan = new WorkPlan();
        var description = getRandString(10);
        var duration = getRandDuration();
        workPlan.setDescription(description);
        workPlan.setDuration(duration);
        workPlanDBDao.create(workPlan);

        var workPlans = workPlanDBDao.findAll();
        assertEquals(dataBaseSize + 1, workPlans.size());
        // get workPlan with the set index
        for (var gotWorkPlan : workPlans) {
            if (gotWorkPlan.getWorkPlanId() == workPlan.getWorkPlanId()) {
                assertEquals(description, gotWorkPlan.getDescription());
                assertEquals(duration, gotWorkPlan.getDuration());
            }
        }
        dataBaseSize++;
    }

    @Test
    public void testRead() throws Exception {
        var workPlan = new WorkPlan();
        var description = getRandString(10);
        var duration = getRandDuration();
        workPlan.setDescription(description);
        workPlan.setDuration(duration);
        workPlanDBDao.create(workPlan);

        var gotWorkPlan = workPlanDBDao.read(workPlan.getWorkPlanId());
        assertEquals(description, gotWorkPlan.getDescription());
        assertEquals(duration, gotWorkPlan.getDuration());
    }

    @Test
    public void testUpdate() throws Exception {
        var workPlan = new WorkPlan();
        var description = getRandString(10);
        var duration = getRandDuration();
        workPlan.setDescription(description);
        workPlan.setDuration(duration);
        workPlanDBDao.create(workPlan);

        var workPlans = workPlanDBDao.findAll();
        assertEquals(dataBaseSize + 1, workPlans.size());
        for (var gotWorkPlan : workPlans) {
            if (gotWorkPlan.getWorkPlanId() == workPlan.getWorkPlanId()) {
                assertEquals(description, gotWorkPlan.getDescription());
                assertEquals(duration, gotWorkPlan.getDuration());
            }
        }

        var updatedDescription = getRandString(10);
        var updatedDuration = getRandDuration();
        workPlan.setDescription(updatedDescription);
        workPlan.setDuration(updatedDuration);
        workPlanDBDao.update(workPlan);

        workPlans = workPlanDBDao.findAll();
        assertEquals(dataBaseSize + 1, workPlans.size());
        for (var gotWorkPlan : workPlans) {
            if (gotWorkPlan.getWorkPlanId() == workPlan.getWorkPlanId()) {
                assertEquals(updatedDescription, gotWorkPlan.getDescription());
                assertEquals(updatedDuration, gotWorkPlan.getDuration());
            }
        }
    }

    @Test
    public void testDelete() throws Exception {
        var workPlan = new WorkPlan();
        var description = getRandString(10);
        var duration = getRandDuration();
        workPlan.setDescription(description);
        workPlan.setDuration(duration);
        workPlanDBDao.create(workPlan);

        var workPlans = workPlanDBDao.findAll();
        assertEquals(dataBaseSize + 1, workPlans.size());
        for (var gotWorkPlan : workPlans) {
            if (gotWorkPlan.getWorkPlanId() == workPlan.getWorkPlanId()) {
                assertEquals(description, gotWorkPlan.getDescription());
                assertEquals(duration, gotWorkPlan.getDuration());
            }
        }

        workPlanDBDao.delete(workPlan.getWorkPlanId());
        workPlans = workPlanDBDao.findAll();
        assertEquals(dataBaseSize, workPlans.size());
    }

    @Test
    public void testFindAll() throws Exception {
        var workPlans = workPlanDBDao.findAll();
        assertEquals(dataBaseSize, workPlans.size());
    }

    @AfterEach
    public void tearDown() throws Exception {
        var manager = DAOManager.getInstance();
        manager.close();
    }
}
