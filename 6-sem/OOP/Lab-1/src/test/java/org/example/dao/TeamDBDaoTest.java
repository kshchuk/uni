package org.example.dao;

import org.example.dao.db.DAOManager;
import org.example.entity.Team;
import org.junit.jupiter.api.*;

import java.sql.SQLException;

import static org.junit.jupiter.api.Assertions.*;

public class TeamDBDaoTest {
    private TeamDao teamDBDao;
    private SpecialistDao specialistDBDao;
    private WorkPlanDao workPlanDBDao;
    private int dataBaseSize;

    @BeforeEach
    public void setUp() throws Exception {
        var manager = DAOManager.getInstance();
        teamDBDao = (TeamDao) manager.getDAO(DAOManager.Table.TEAM);
        specialistDBDao = (SpecialistDao) manager.getDAO(DAOManager.Table.SPECIALIST);
        workPlanDBDao = (WorkPlanDao) manager.getDAO(DAOManager.Table.WORKPLAN);
        dataBaseSize = teamDBDao.findAll().size();
    }

    @Test
    public void testCreate() throws Exception {
        var team = new Team();
        var specialists = specialistDBDao.findAll();
        var workPlans = workPlanDBDao.findAll();
        var specialistId = specialists.get((int) (Math.random() * specialists.size())).getSpecialistId();
        var workPlanId = workPlans.get((int) (Math.random() * workPlans.size())).getWorkPlanId();
        team.getDispatcher().setSpecialistId(specialistId);
        team.getWorkPlan().setWorkPlanId(workPlanId);

        teamDBDao.create(team);
        var teams = teamDBDao.findAll();

        assertEquals(dataBaseSize + 1, teams.size());
        // get team with the set index
        for (var gotTeam : teams) {
            if (gotTeam.getTeamId() == team.getTeamId()) {
                assertEquals(specialistId, gotTeam.getDispatcher().getSpecialistId());
                assertEquals(workPlanId, gotTeam.getWorkPlan().getWorkPlanId());
            }
        }
        dataBaseSize++;
    }

    @Test
    public void testRead() throws Exception {
        var team = new Team();
        var specialists = specialistDBDao.findAll();
        var workPlans = workPlanDBDao.findAll();
        var specialistId = specialists.get((int) (Math.random() * specialists.size())).getSpecialistId();
        var workPlanId = workPlans.get((int) (Math.random() * workPlans.size())).getWorkPlanId();
        team.getDispatcher().setSpecialistId(specialistId);
        team.getWorkPlan().setWorkPlanId(workPlanId);

        teamDBDao.create(team);
        var gotTeam = teamDBDao.read(team.getTeamId());
        assertEquals(specialistId, gotTeam.getDispatcher().getSpecialistId());
        assertEquals(workPlanId, gotTeam.getWorkPlan().getWorkPlanId());
    }

    @Test
    public void testUpdate() throws Exception {
        var team = new Team();
        var specialists = specialistDBDao.findAll();
        var workPlans = workPlanDBDao.findAll();
        var specialistId = specialists.get((int) (Math.random() * specialists.size())).getSpecialistId();
        var workPlanId = workPlans.get((int) (Math.random() * workPlans.size())).getWorkPlanId();
        team.getDispatcher().setSpecialistId(specialistId);
        team.getWorkPlan().setWorkPlanId(workPlanId);

        teamDBDao.create(team);
        var gotTeam = teamDBDao.read(team.getTeamId());
        assertEquals(specialistId, gotTeam.getDispatcher().getSpecialistId());
        assertEquals(workPlanId, gotTeam.getWorkPlan().getWorkPlanId());

        var updatedSpecialistId = specialists.get((int) (Math.random() * specialists.size())).getSpecialistId();
        var updatedWorkPlanId = workPlans.get((int) (Math.random() * workPlans.size())).getWorkPlanId();
        gotTeam.getDispatcher().setSpecialistId(updatedSpecialistId);
        gotTeam.getWorkPlan().setWorkPlanId(updatedWorkPlanId);
        teamDBDao.update(gotTeam);

        var updatedTeam = teamDBDao.read(gotTeam.getTeamId());
        assertEquals(updatedSpecialistId, updatedTeam.getDispatcher().getSpecialistId());
        assertEquals(updatedWorkPlanId, updatedTeam.getWorkPlan().getWorkPlanId());
    }

    @Test
    public void testDelete() throws Exception {
        var team = new Team();
        var specialists = specialistDBDao.findAll();
        var workPlans = workPlanDBDao.findAll();
        var specialistId = specialists.get((int) (Math.random() * specialists.size())).getSpecialistId();
        var workPlanId = workPlans.get((int) (Math.random() * workPlans.size())).getWorkPlanId();
        team.getDispatcher().setSpecialistId(specialistId);
        team.getWorkPlan().setWorkPlanId(workPlanId);

        teamDBDao.create(team);
        var teams = teamDBDao.findAll();
        assertEquals(dataBaseSize + 1, teams.size());
        for (var gotTeam : teams) {
            if (gotTeam.getTeamId() == team.getTeamId()) {
                assertEquals(specialistId, gotTeam.getDispatcher().getSpecialistId());
                assertEquals(workPlanId, gotTeam.getWorkPlan().getWorkPlanId());
            }
        }

        teamDBDao.delete(team.getTeamId());
        teams = teamDBDao.findAll();
        assertEquals(dataBaseSize, teams.size());
        for (var gotTeam : teams) {
            assertNotEquals(team.getTeamId(), gotTeam.getTeamId());
        }
    }

    @Test
    public void testFindAll() throws Exception {
        var teams = teamDBDao.findAll();
        for (var team : teams) {
            assertNotNull(team.getTeamId());
            assertNotNull(team.getDispatcher().getSpecialistId());
            assertNotNull(team.getWorkPlan().getWorkPlanId());
        }
    }

    @AfterEach
    public void tearDown() throws SQLException {
        var manager = DAOManager.getInstance();
        manager.close();
    }
}
