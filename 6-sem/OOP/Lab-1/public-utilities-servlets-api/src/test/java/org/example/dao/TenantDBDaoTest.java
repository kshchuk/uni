package org.example.dao;

import org.example.dao.db.DAOManager;
import org.example.entity.Tenant;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import static org.example.Utils.getRandString;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;

public class TenantDBDaoTest {
    private TenantDao tenantDBDao;
    private int initialDatabaseSize;

    @BeforeEach
    public void setUp() throws Exception {
        initializeDaoObjects();
        initialDatabaseSize = tenantDBDao.findAll().size();
    }

    private void initializeDaoObjects() throws Exception {
        var manager = DAOManager.getInstance();
        tenantDBDao = (TenantDao) manager.getDAO(DAOManager.Table.TENANT);
    }

    @Test
    public void testCreate() throws Exception {
        Tenant tenant = createTenant();
        tenantDBDao.create(tenant);
        verifyTenantCreation(tenant);
        initialDatabaseSize++;
    }

    private Tenant createTenant() {
        Tenant tenant = new Tenant();
        tenant.setName(getRandString(10));
        tenant.setAddress(getRandString(10));
        return tenant;
    }

    private void verifyTenantCreation(Tenant tenant) throws Exception {
        var tenants = tenantDBDao.findAll();
        assertEquals(initialDatabaseSize + 1, tenants.size());
        verifyTenantDetails(tenant, tenants);
    }

    private void verifyTenantDetails(Tenant tenant, Iterable<Tenant> tenants) {
        for (Tenant gotTenant : tenants) {
            if (gotTenant.getTenantId() == tenant.getTenantId()) {
                assertEquals(tenant.getName(), gotTenant.getName());
                assertEquals(tenant.getAddress(), gotTenant.getAddress());
            }
        }
    }

    @Test
    public void testUpdate() throws Exception {
        Tenant tenant = createTenant();
        tenantDBDao.create(tenant);
        verifyTenantCreation(tenant);

        var updatedTenant = createTenant();
        updatedTenant.setTenantId(tenant.getTenantId());
        tenantDBDao.update(updatedTenant);

        var tenants = tenantDBDao.findAll();
        assertEquals(initialDatabaseSize + 1, tenants.size());
        verifyTenantDetails(updatedTenant, tenants);
    }

    @Test
    public void testDelete() throws Exception {
        Tenant tenant = createTenant();
        tenantDBDao.create(tenant);
        verifyTenantCreation(tenant);

        tenantDBDao.delete(tenant.getTenantId());
        var tenants = tenantDBDao.findAll();
        assertEquals(initialDatabaseSize, tenants.size());
    }

    @Test
    public void testFindAll() throws Exception {
        var tenants = tenantDBDao.findAll();
        assertEquals(initialDatabaseSize, tenants.size());
    }

    @Test
    public void testRead() throws Exception {
        Tenant tenant = createTenant();
        tenantDBDao.create(tenant);

        var gotTenant = tenantDBDao.read(tenant.getTenantId());
        assertNotNull(gotTenant);
        assertEquals(tenant.getName(), gotTenant.getName());
        assertEquals(tenant.getAddress(), gotTenant.getAddress());
    }

    @AfterAll
    public static void tearDown() throws Exception {
        DAOManager.getInstance().close();
    }
}
