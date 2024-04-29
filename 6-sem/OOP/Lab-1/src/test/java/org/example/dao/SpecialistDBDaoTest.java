package org.example.dao;

import org.example.dao.db.DAOManager;
import org.example.entity.Specialist;
import org.example.entity.Team;
import org.junit.jupiter.api.*;
import java.util.List;
import static org.example.Utils.*;
import static org.junit.jupiter.api.Assertions.*;

public class SpecialistDBDaoTest {
    private SpecialistDao specialistDBDao;
    private TeamDao teamDBDao;
    private int dataBaseSize;

    @BeforeEach
    public void setUp() throws Exception {
        var manager = DAOManager.getInstance();
        specialistDBDao = (SpecialistDao) manager.getDAO(DAOManager.Table.SPECIALIST);
        teamDBDao = (TeamDao) manager.getDAO(DAOManager.Table.TEAM);
        dataBaseSize = specialistDBDao.findAll().size();
    }

    @Test
    public void testCreate() throws Exception {
        Specialist specialist = getRandomSpecialist(null);
        specialistDBDao.create(specialist);
        verifySpecialistCreation(specialist);
        dataBaseSize++;
    }

    private void verifySpecialistCreation(Specialist specialist) throws Exception {
        List<Specialist> specialists = specialistDBDao.findAll();
        assertEquals(dataBaseSize + 1, specialists.size());
        verifySpecialistDetails(specialist, specialists);
    }

    private void verifySpecialistDetails(Specialist specialist, List<Specialist> specialists) {
        for (Specialist gotSpecialist : specialists) {
            if (gotSpecialist.getSpecialistId() == specialist.getSpecialistId()) {
                assertEquals(specialist.getName(), gotSpecialist.getName());
                assertEquals(specialist.getSpecialization(), gotSpecialist.getSpecialization());
            }
        }
    }

    @Test
    public void testRead() throws Exception {
        Specialist specialist = getRandomSpecialist(null);
        specialistDBDao.create(specialist);
        Specialist gotSpecialist = specialistDBDao.read(specialist.getSpecialistId());
        assertEquals(specialist.getName(), gotSpecialist.getName());
        assertEquals(specialist.getSpecialization(), gotSpecialist.getSpecialization());
    }

    @Test
    public void testUpdate() throws Exception {
        Specialist specialist = getRandomSpecialist(null);
        specialistDBDao.create(specialist);
        verifySpecialistCreation(specialist);
        dataBaseSize++;
    }

    @Test
    public void testDelete() throws Exception {
        Specialist specialist = getRandomSpecialist(null);
        specialistDBDao.create(specialist);
        verifySpecialistCreation(specialist);

        specialistDBDao.delete(specialist.getSpecialistId());
        List<Specialist> specialists = specialistDBDao.findAll();
        assertEquals(dataBaseSize, specialists.size());
        assertSpecialistDeleted(specialist, specialists);
    }

    private void assertSpecialistDeleted(Specialist specialist, List<Specialist> specialists) {
        for (Specialist gotSpecialist : specialists) {
            assertNotEquals(specialist.getSpecialistId(), gotSpecialist.getSpecialistId());
        }
    }

    @Test
    public void testFindAll() throws Exception {
        List<Specialist> specialists = specialistDBDao.findAll();
        assertEquals(dataBaseSize, specialists.size());
    }

    @Test
    public void testFindByTeamId() throws Exception {
        Specialist dispatcher = getRandomSpecialist(null);
        specialistDBDao.create(dispatcher);
        Team team = getRandomTeam(dispatcher);
        teamDBDao.create(team);
        Specialist specialist = getRandomSpecialist(team);
        specialistDBDao.create(specialist);
        dataBaseSize += 2;

        specialist.getTeam().setDispatcher(null);
        List<Specialist> specialists = specialistDBDao.findByTeamId(team.getTeamId());
        assertEquals(1, specialists.size());
        assertEquals(specialist, specialists.get(0));
    }

    @AfterAll
    public static void tearDown() throws Exception {
        DAOManager.getInstance().close();
    }
}
