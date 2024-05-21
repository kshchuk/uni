package org.example.servlet;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.example.dto.WorkPlanDTO;
import org.example.entity.Specialist;
import org.example.entity.WorkPlan;
import org.example.mapper.WorkPlanMapper;
import org.example.repository.SpecialistRepository;
import org.example.repository.TeamRepository;
import org.example.repository.WorkPlanRepository;
import org.example.repository.impl.SpecialistRepositoryImpl;
import org.example.repository.impl.TeamRepositoryImpl;
import org.example.repository.impl.WorkPlanRepositoryImpl;
import org.example.service.DispatcherService;
import org.example.service.impl.DispatcherServiceImpl;

import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.io.PrintWriter;
import java.util.List;
import java.util.UUID;
import java.util.logging.Logger;

@WebServlet(name = "dispatcherServlet", value = "/dispatcher/*")
public class DispatcherServlet extends HttpServlet {
    Logger logger = Logger.getLogger(SpecialistServlet.class.getName());
    ObjectMapper objectMapper = new ObjectMapper();
    private DispatcherService dispatcherService;

    public void init() {
        SpecialistRepository specialistRepository = new SpecialistRepositoryImpl();
        TeamRepository teamRepository = new TeamRepositoryImpl();
        WorkPlanRepository workPlanRepository = new WorkPlanRepositoryImpl();
        dispatcherService = new DispatcherServiceImpl(specialistRepository, teamRepository, workPlanRepository);
    }

    public void doGet(HttpServletRequest request, HttpServletResponse response) throws IOException {
        response.setContentType("application/json");
        PrintWriter out = response.getWriter();

        logger.info("GET request to SpecialistServlet" + request.getPathInfo());

        String pathInfo = request.getPathInfo();
        if (pathInfo != null) {
            // Handle the case for GET /dispatcher/workplans?id=...
            if (pathInfo.startsWith("/workplans")) {
                String id = request.getParameter("id");

                if (id == null) {
                    response.setStatus(HttpServletResponse.SC_BAD_REQUEST);
                    return;
                }

                Specialist specialist = dispatcherService.get(UUID.fromString(id));
                if (specialist == null) {
                    response.setStatus(HttpServletResponse.SC_NOT_FOUND);
                    return;
                }

                List<WorkPlan> workPlans = dispatcherService.getWorkPlans(UUID.fromString(id));
                List<WorkPlanDTO> workPlanDTOs = workPlans.stream()
                        .map(WorkPlanMapper.INSTANCE::toDto)
                        .toList();
                String jsonResponse = objectMapper.writeValueAsString(workPlanDTOs);
                out.write(jsonResponse);

                response.setStatus(HttpServletResponse.SC_OK);
            }
        }
    }
}
