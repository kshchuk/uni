package org.example.servlet;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.example.dto.SpecialistDTO;
import org.example.dto.TeamDTO;
import org.example.dto.WorkPlanDTO;
import org.example.entity.Specialist;
import org.example.entity.Team;
import org.example.entity.WorkPlan;
import org.example.mapper.SpecialistMapper;
import org.example.mapper.TeamMapper;
import org.example.mapper.WorkPlanMapper;
import org.example.repository.TeamRepository;
import org.example.repository.impl.TeamRepositoryImpl;
import org.example.service.TeamService;
import org.example.service.impl.TeamServiceImpl;

import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.io.PrintWriter;
import java.util.List;
import java.util.UUID;
import java.util.logging.Logger;

@WebServlet(name = "teamServlet", value = "/team*")
public class TeamServlet extends HttpServlet {
    Logger logger = Logger.getLogger(TeamServlet.class.getName());
    ObjectMapper objectMapper = new ObjectMapper();
    private TeamService teamService;

    public void init() {
        TeamRepository teamRepository = new TeamRepositoryImpl();
        teamService = new TeamServiceImpl(teamRepository);
    }

    public void doGet(HttpServletRequest request, HttpServletResponse response) throws IOException {
        response.setContentType("application/json");
        PrintWriter out = response.getWriter();

        logger.info("GET request to TeamServlet" + request.getPathInfo());

        String pathInfo = request.getPathInfo();
        if (pathInfo != null) {
            // Handle the case for "GET /team/all"
            if (pathInfo.equals("/all")) {
                List<Team> teams = teamService.getAll();
                List<TeamDTO> teamDTOs = teams.stream()
                        .map(TeamMapper.INSTANCE::toDto)
                        .toList();

                String jsonResponse = objectMapper.writeValueAsString(teamDTOs);
                out.write(jsonResponse);

                response.setStatus(HttpServletResponse.SC_OK);
            }

            else if (pathInfo.equals("/specialists")) {
                String id = request.getParameter("id");

                if (id == null) {
                    response.setStatus(HttpServletResponse.SC_BAD_REQUEST);
                    return;
                }

                List<Specialist> specialists = teamService.getSpecialists(UUID.fromString(id));
                List<SpecialistDTO> specialistDTOs = specialists.stream()
                        .map(SpecialistMapper.INSTANCE::toDto)
                        .toList();

                String jsonResponse = objectMapper.writeValueAsString(specialistDTOs);
                out.write(jsonResponse);

                response.setStatus(HttpServletResponse.SC_OK);
            }

            else if (pathInfo.equals("/workplans")) {
                String id = request.getParameter("id");

                if (id == null) {
                    response.setStatus(HttpServletResponse.SC_BAD_REQUEST);
                    return;
                }

                List<WorkPlan> workPlans = teamService.getWorkPlans(UUID.fromString(id));
                List<WorkPlanDTO> workPlanDTOs = workPlans.stream()
                        .map(WorkPlanMapper.INSTANCE::toDto)
                        .toList();

                String jsonResponse = objectMapper.writeValueAsString(workPlanDTOs);
                out.write(jsonResponse);

                response.setStatus(HttpServletResponse.SC_OK);
            }

            // Handle the case for GET /team?id=...
            else {
                String id = request.getParameter("id");

                if (id == null) {
                    response.setStatus(HttpServletResponse.SC_BAD_REQUEST);
                    return;
                }

                Team team = teamService.get(UUID.fromString(id));

                if (team == null) {
                    response.setStatus(HttpServletResponse.SC_NOT_FOUND);
                    return;
                }

                TeamDTO teamDTO = TeamMapper.INSTANCE.toDto(team);

                String jsonResponse = objectMapper.writeValueAsString(teamDTO);
                out.write(jsonResponse);

                response.setStatus(HttpServletResponse.SC_OK);
            }
        } else {
            response.setStatus(HttpServletResponse.SC_BAD_REQUEST);
        }
    }

    public void doPost(HttpServletRequest request, HttpServletResponse response) throws IOException {
        response.setContentType("application/json");
        String body = request.getReader().lines().reduce("", (accumulator, actual) -> accumulator + actual);

        logger.info("POST request to TeamServlet" + request.getPathInfo());

        if (body.isEmpty()) {
            response.setStatus(HttpServletResponse.SC_BAD_REQUEST);
            return;
        }

        TeamDTO teamDTO;
        try {
            teamDTO = objectMapper.readValue(body, TeamDTO.class);
        } catch (JsonProcessingException e) {
            response.setStatus(HttpServletResponse.SC_BAD_REQUEST);
            return;
        }
        Team team = TeamMapper.INSTANCE.toEntity(teamDTO);
        teamService.create(team);

        response.setStatus(HttpServletResponse.SC_CREATED);
    }

    public void doDelete(HttpServletRequest request, HttpServletResponse response) throws IOException {
        response.setContentType("application/json");
        String pathInfo = request.getPathInfo();

        logger.info("DELETE request to TeamServlet" + pathInfo);

        if (pathInfo != null) {
            String id = request.getParameter("id");

            if (id == null) {
                response.setStatus(HttpServletResponse.SC_BAD_REQUEST);
                return;
            }

            boolean isDeleted = teamService.delete(UUID.fromString(id));
            if (isDeleted) {
                response.setStatus(HttpServletResponse.SC_OK);
            } else {
                response.setStatus(HttpServletResponse.SC_NOT_FOUND);
            }
        } else {
            response.setStatus(HttpServletResponse.SC_BAD_REQUEST);
        }
    }

    public void doPut(HttpServletRequest request, HttpServletResponse response) throws IOException {
        response.setContentType("application/json");
        String body = request.getReader().lines().reduce("", (accumulator, actual) -> accumulator + actual);

        logger.info("PUT request to TeamServlet" + request.getPathInfo());

        if (body.isEmpty()) {
            response.setStatus(HttpServletResponse.SC_BAD_REQUEST);
            return;
        }

        TeamDTO teamDTO;
        try {
            teamDTO = objectMapper.readValue(body, TeamDTO.class);
        } catch (JsonProcessingException e) {
            response.setStatus(HttpServletResponse.SC_BAD_REQUEST);
            return;
        }

        Team team = TeamMapper.INSTANCE.toEntity(teamDTO);
        Team oldTeam = teamService.get(UUID.fromString(teamDTO.getTeamId()));
        if (oldTeam == null) {
            teamService.create(team);
            response.setStatus(HttpServletResponse.SC_CREATED);
        } else {
            teamService.update(team);
            response.setStatus(HttpServletResponse.SC_OK);
        }
    }
}
