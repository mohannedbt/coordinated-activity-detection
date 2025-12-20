using Behavior_risk_UI.mappers;
using Behavior_risk_UI.Models;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace Behavior_risk_UI.Controllers;
[Authorize]

public class DashboardController : Controller
{
    private readonly ApiClient _apiService;

    public DashboardController(ApiClient apiService)
    {
        _apiService = apiService;
    }

    // Main Dashboard
    public async Task<IActionResult> Index()
    {
        var data = await _apiService.GetDashboardAsync();
        var model = DashboardMapper.Build(data);
        return View(model);
    }

    // Account Risks Page
    public async Task<IActionResult> Accounts()
    {
        var data = await _apiService.GetDashboardAsync();
        var model = DashboardMapper.Build(data);
        return View("AccountRisks", model);
    }

    // Action Logs Page
    public async Task<IActionResult> Logs()
    {
        var data = await _apiService.GetDashboardAsync();
        var model = DashboardMapper.Build(data);
        return View("ActionLogs", model);
    }

    // System Settings Page
    public async Task<IActionResult> Settings()
    {
        var data = await _apiService.GetDashboardAsync();
        var model = DashboardMapper.Build(data);
        return View("Settings", model);
    }
}