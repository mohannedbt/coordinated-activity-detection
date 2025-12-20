using System.Text.Json;
using Behavior_risk_UI.Models;

namespace Behavior_risk_UI.mappers
{
    public static class DashboardMapper
    {
        public static DashboardViewModel Build(ApiPayload payload)
        {
            // Define options to respect the [JsonPropertyName] attributes
            var options = new JsonSerializerOptions
            {
                PropertyNamingPolicy = null, // Uses the attributes exactly as defined
                WriteIndented = false
            };

            if (payload == null) return new DashboardViewModel();

            var posts = payload.Posts ?? new List<PostDto>();
            var accounts = payload.Accounts ?? new List<AccountDto>();

            return new DashboardViewModel
            {
                TotalPosts = payload.Summary?.TotalPosts ?? posts.Count,
                AutoActions = payload.Summary?.AutoActions ?? posts.Count(p => p.Decision == "AUTO_ACTION"),
                QueueReviews = payload.Summary?.QueueReview ?? posts.Count(p => p.Decision == "QUEUE_REVIEW"),
                TopAccounts = accounts.OrderByDescending(a => a.AvgRisk).Take(10).ToList(),
                AccountsJson = JsonSerializer.Serialize(accounts, options),
                AvgRisk = posts.Any() ? Math.Round(posts.Average(p => p.RiskScore), 2) : 0,

                // CRITICAL FIX: Serialize the list into a string for the View
                PostsJson = JsonSerializer.Serialize(posts, options),

                DecisionCounts = posts
                    .GroupBy(p => p.Decision ?? "Unknown")
                    .ToDictionary(g => g.Key, g => g.Count()),

                ReasonCounts = posts
                    .GroupBy(p => p.ReasonCategory ?? "Unknown")
                    .ToDictionary(g => g.Key, g => g.Count()),

                TopRiskPosts = posts
                    .OrderByDescending(p => p.RiskScore)
                    .Take(5)
                    .Select(p => new PostCardViewModel
                    {
                        PostId = p.PostId,
                        Text = p.Text ?? "No Content",
                        RiskScore = p.RiskScore,
                        Confidence = p.Confidence,
                        Decision = p.Decision
                    })
                    .ToList()
            };
        }
    }
}