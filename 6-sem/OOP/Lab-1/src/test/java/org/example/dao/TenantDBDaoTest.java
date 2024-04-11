package org.example.dao;

import org.example.dao.db.DAOManager;
import org.example.entity.Tenant;
import org.junit.jupiter.api.*;

import static org.example.Utils.getRandString;
import static org.junit.jupiter.api.Assertions.*;


public class TenantDBDaoTest {
        private TenantDao tenantDBDao;
        private int dataBaseSize;

        @BeforeEach
        public void setUp() throws Exception {
            var manager = DAOManager.getInstance();
            tenantDBDao = (TenantDao) manager.getDAO(DAOManager.Table.TENANT);
            dataBaseSize = tenantDBDao.findAll().size();
        }

        @Test
        public void testCreate() throws Exception {
            var tenant = new Tenant();
            var name = getRandString(10);
            var address = getRandString(10);
            tenant.setName(name);
            tenant.setAddress(address);

            tenantDBDao.create(tenant);
            var tenants = tenantDBDao.findAll();

            assertEquals(dataBaseSize + 1, tenants.size());
            // get tenant with the set index
            for (var gotTenant : tenants) {
                if (gotTenant.getTenantId() == tenant.getTenantId()) {
                    assertEquals(name, gotTenant.getName());
                    assertEquals(address, gotTenant.getAddress());
                }
            }
            dataBaseSize++;
        }

        @Test
        public void testUpdate() throws Exception {
            var tenant = new Tenant();
            var name = getRandString(10);
            var address = getRandString(10);
            tenant.setName(name);
            tenant.setAddress(address);

            tenantDBDao.create(tenant);
            var tenants = tenantDBDao.findAll();
            assertEquals(dataBaseSize + 1, tenants.size());
            for (var gotTenant : tenants) {
                if (gotTenant.getTenantId() == tenant.getTenantId()) {
                    assertEquals(name, gotTenant.getName());
                    assertEquals(address, gotTenant.getAddress());
                }
            }

            var updatedName = getRandString(10);
            var updatedAddress = getRandString(10);

            tenant.setName(updatedName);
            tenant.setAddress(updatedAddress);
            tenantDBDao.update(tenant);

            tenants = tenantDBDao.findAll();
            assertEquals(dataBaseSize + 1, tenants.size());
            for (var gotTenant : tenants) {
                if (gotTenant.getTenantId() == tenant.getTenantId()) {
                    assertEquals(updatedName, gotTenant.getName());
                    assertEquals(updatedAddress, gotTenant.getAddress());
                }
            }
        }

        @Test
        public void testDelete() throws Exception {
            var tenant = new Tenant();
            var name = getRandString(10);
            var address = getRandString(10);
            tenant.setName(name);
            tenant.setAddress(address);

            tenantDBDao.create(tenant);
            var tenants = tenantDBDao.findAll();
            assertEquals(dataBaseSize + 1, tenants.size());

            tenantDBDao.delete(tenant.getTenantId());
            tenants = tenantDBDao.findAll();
            assertEquals(dataBaseSize, tenants.size());
        }

        @Test
        public void testFindAll() throws Exception {
            var tenants = tenantDBDao.findAll();
            assertEquals(dataBaseSize, tenants.size());
        }

        @Test
        public void testRead() throws Exception {
            var tenant = new Tenant();
            var name = getRandString(10);
            var address = getRandString(10);
            tenant.setName(name);
            tenant.setAddress(address);

            tenantDBDao.create(tenant);
            var gotTenant = tenantDBDao.read(tenant.getTenantId());
            assertNotNull(gotTenant);
            assertEquals(name, gotTenant.getName());
            assertEquals(address, gotTenant.getAddress());
        }

        @AfterAll
        public static void tearDown() throws Exception {
            var manager = DAOManager.getInstance();
            manager.close();
        }
}
