package org.example.dao;

import org.example.dao.db.DAOManager;
import org.example.entity.Specialist;
import org.example.entity.Team;
import org.junit.jupiter.api.*;
import java.util.List;
import java.util.Random;
import static org.junit.jupiter.api.Assertions.*;

public class TeamDBDaoTest {
    private TeamDao teamDBDao;
    private SpecialistDao specialistDBDao;
    private int initialDatabaseSize;

    @BeforeEach
    public void setUp() throws Exception {
        var manager = DAOManager.getInstance();
        teamDBDao = (TeamDao) manager.getDAO(DAOManager.Table.TEAM);
        specialistDBDao = (SpecialistDao) manager.getDAO(DAOManager.Table.SPECIALIST);
        initialDatabaseSize = teamDBDao.findAll().size();
    }

    @Test
    public void testCreate() throws Exception {
        Team team = createTeamWithRandomDispatcher();
        teamDBDao.create(team);
        verifyTeamCreation(team);
        initialDatabaseSize++;
    }

    private Team createTeamWithRandomDispatcher() throws Exception {
        Team team = new Team();
        List<Specialist> specialists = specialistDBDao.findAll();
        if (!specialists.isEmpty()) {
            Specialist randomSpecialist = specialists.get(new Random().nextInt(specialists.size()));
            team.setDispatcher(randomSpecialist);
        }
        return team;
    }

    private void verifyTeamCreation(Team team) throws Exception {
        List<Team> teams = teamDBDao.findAll();
        assertEquals(initialDatabaseSize + 1, teams.size());
        verifyTeamDispatcher(team, teams);
    }

    private void verifyTeamDispatcher(Team team, List<Team> teams) {
        for (Team gotTeam : teams) {
            if (gotTeam.getTeamId() == team.getTeamId()) {
                assertEquals(team.getDispatcher().getSpecialistId(), gotTeam.getDispatcher().getSpecialistId());
            }
        }
    }

    @Test
    public void testRead() throws Exception {
        Team team = createTeamWithRandomDispatcher();
        teamDBDao.create(team);
        Team gotTeam = teamDBDao.read(team.getTeamId());
        assertEquals(team.getDispatcher().getSpecialistId(), gotTeam.getDispatcher().getSpecialistId());
    }

    @Test
    public void testUpdate() throws Exception {
        Team team = createTeamWithRandomDispatcher();
        teamDBDao.create(team);
        Team gotTeam = teamDBDao.read(team.getTeamId());
        assertEquals(team.getDispatcher().getSpecialistId(), gotTeam.getDispatcher().getSpecialistId());

        Specialist updatedSpecialist = getRandomSpecialist();
        gotTeam.setDispatcher(updatedSpecialist);
        teamDBDao.update(gotTeam);

        Team updatedTeam = teamDBDao.read(gotTeam.getTeamId());
        assertEquals(updatedSpecialist.getSpecialistId(), updatedTeam.getDispatcher().getSpecialistId());
    }

    private Specialist getRandomSpecialist() throws Exception {
        List<Specialist> specialists = specialistDBDao.findAll();
        if (!specialists.isEmpty()) {
            return specialists.get(new Random().nextInt(specialists.size()));
        }
        return null;
    }

    @Test
    public void testDelete() throws Exception {
        Team team = createTeamWithRandomDispatcher();
        teamDBDao.create(team);
        List<Team> teams = teamDBDao.findAll();
        assertEquals(initialDatabaseSize + 1, teams.size());
        verifyTeamDispatcher(team, teams);

        teamDBDao.delete(team.getTeamId());
        teams = teamDBDao.findAll();
        assertEquals(initialDatabaseSize, teams.size());
        assertTeamDeleted(team, teams);
    }

    private void assertTeamDeleted(Team team, List<Team> teams) {
        for (Team gotTeam : teams) {
            assertNotEquals(team.getTeamId(), gotTeam.getTeamId());
        }
    }

    @Test
    public void testFindAll() throws Exception {
        List<Team> teams = teamDBDao.findAll();
        for (Team team : teams) {
            assertNotNull(team.getTeamId());
            assertNotNull(team.getDispatcher().getSpecialistId());
        }
    }

    @AfterEach
    public void tearDown() throws Exception {
        DAOManager.getInstance().close();
    }
}
