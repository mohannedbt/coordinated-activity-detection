using System.Text.Json.Serialization;

namespace Behavior_risk_UI.Models;


public class ApiPayload
{
    [JsonPropertyName("posts")]
    public List<PostDto> Posts { get; set; } = new();

    [JsonPropertyName("summary")]
    public ApiSummary Summary { get; set; }

    [JsonPropertyName("accounts")] // New: Added to match your JSON
    public List<AccountDto> Accounts { get; set; } = new();
}

public class PostDto
{
    [JsonPropertyName("post_id")]
    public int PostId { get; set; }

    [JsonPropertyName("text")]
    public string Text { get; set; }

    [JsonPropertyName("risk_score")]
    public double RiskScore { get; set; }

    [JsonPropertyName("confidence")]
    public double Confidence { get; set; }

    [JsonPropertyName("decision")]
    public string Decision { get; set; }

    [JsonPropertyName("reason_category")]
    public string ReasonCategory { get; set; }

    [JsonPropertyName("interpretation")] // Note: This isn't in your JSON sample, check if API provides it
    public string Interpretation { get; set; }
}

public class AccountDto
{
    [JsonPropertyName("account_id")]
    public string AccountId { get; set; }

    [JsonPropertyName("avg_risk")]
    public double AvgRisk { get; set; }

    [JsonPropertyName("total_posts")]
    public int TotalPosts { get; set; }
}
public class ApiSummary
{
    [JsonPropertyName("total_posts")]
    public int TotalPosts { get; set; }

    [JsonPropertyName("auto_actions")]
    public int AutoActions { get; set; }

    [JsonPropertyName("queue_review")]
    public int QueueReview { get; set; }
}
