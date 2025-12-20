using System.Net.Http;
using System.Net.Http.Json;
using Behavior_risk_UI.Models;

public class ApiClient
{
    private readonly HttpClient _http;

    public ApiClient(HttpClient http)
    {
        _http = http;
    }

    public async Task<ApiPayload> GetDashboardAsync()
    {
        var response = await _http.GetAsync("/api/dashboard");

        if (!response.IsSuccessStatusCode)
        {
            throw new Exception("Risk API unavailable");
        }

        var payload = await response.Content.ReadFromJsonAsync<ApiPayload>();

        return payload!;
    }
}