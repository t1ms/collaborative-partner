CARE: An Explainable Computational Framework for Assessing
Client-Perceived Therapeutic Alliance Using Large Language Models
Anqi Li1,2 , Chenxiao Wang2 , Yu Lu2 , Renjun Xu1* , Lizhi Ma3* , Zhenzhong Lan2*
1
Zhejiang University
2
Westlake University
3
Department of Psychology, Jing Hengyi School of Education, Hangzhou Normal University
lianqi, lanzhenzhong@westlake.edu.cn; malizhi@hznu.edu.cn


## Abstract


arXiv:2602.20648v1 [cs.CL] 24 Feb 2026

Client perceptions of the therapeutic alliance
are critical for counseling effectiveness. Accurately capturing these perceptions remains
challenging, as traditional post-session questionnaires are burdensome and often delayed,
while existing computational approaches produce coarse scores, lack interpretable rationales, and fail to model holistic session context.
We present CARE, an LLM-based framework
to automatically predict multi-dimensional alliance scores and generate interpretable rationales from counseling transcripts. Built
on the CounselingWAI dataset and enriched
with 9,516 expert-curated rationales, CARE
is fine-tuned using rationale-augmented supervision with the LLaMA-3.1-8B-Instruct backbone. Experiments show that CARE outperforms leading LLMs and substantially reduces
the gap between counselor evaluations and
client-perceived alliance, achieving over 70%
higher Pearson correlation with client ratings.
Rationale-augmented supervision further improves predictive accuracy. CARE also produces high-quality, contextually grounded rationales, validated by both automatic and human evaluations. Applied to real-world Chinese online counseling sessions, CARE uncovers common alliance-building challenges, illustrates how interaction patterns shape alliance
development, and provides actionable insights,
demonstrating its potential as an AI-assisted
tool for supporting mental health care.

1


## Introduction


The therapeutic alliance—the collaborative relationship between counselor and client—is one
of the strongest predictors of counseling outcomes (Martin et al., 2000; Lambert and Barley,
2001). Within this relationship, clients’ perceptions
are particularly crucial, with studies showing they
robustly correlate more strongly with treatment success compared to counselor assessments (Horvath
and Symonds, 1991; Piper et al., 1991). Moreover,

Did you try the record three small achievements
exercise this week?
No... I don't feel like it would change anything.
I understand your concern. But this exercise
could be the first step to help us find motivation.
I want to know what I'm really living for. Can
this method help me answer that question?
If we don't start with small steps, the bigger
issues will be hard to tackle.
You don‘t understand what I’m going through...

The client seeks meaning, but the
counselor is stuck on modifying immediate
behaviors.
The counselor insists on exercises that
the client believes are futile.
Verbal understanding from the counselor
lacks true empathy, leaving the client feeling
misunderstood.

Figure 1: The CARE model predicts client-perceived
fine-grained working alliance scores after counseling
sessions by identifying and summarizing explanatory
reasons from the dialogue, compared to the traditional
method where clients only provide scores through questionnaires.

discrepancies in their perceptions may compromise
the effectiveness of therapeutic interventions (Horvath et al., 2011).
However, accurately capturing client perspectives remains a major challenge in counseling practice. Traditional methods primarily rely on postsession questionnaires, which can impose burdens
on clients and are often completed irregularly or
with delays (Goldberg et al., 2020). Recent computational approaches have attempted to automatically assess therapeutic alliance from counseling
transcripts (Martinez et al., 2019; Goldberg et al.,
2020; Lin et al., 2023). Yet these approaches face
three key limitations: they typically generate global

---

alliance scores while overlooking the multidimensional nature of the therapeutic relationship (Martinez et al., 2019; Goldberg et al., 2020); provide
only numerical scores without explanatory rationales (Ryu et al., 2021; Goldberg et al., 2020);
and analyze individual conversation turns in isolation rather than capturing holistic therapeutic context (Lin et al., 2023). These gaps restrict the practical utility of AI-driven assessments for guiding
counseling practice.
To address these limitations, we introduce
CARE1 , an LLM-based framework that predicts
fine-grained dimensions of client-perceived therapeutic alliance while generating interpretable rationales. CARE is developed under a rationaleaugmented supervision paradigm, which injects
expert knowledge into the learning process, and incorporates multi-dimensional reasoning to capture
associations between session context and specific
alliance elements. To support this approach, we enrich the CounselingWAI dataset (Li et al., 2024)—
originally comprising Chinese text-based counseling sessions with post-session client ratings across
three core dimensions: shared goals, coordinated
pathways, and emotional attachment—by adding
9,516 expert-annotated rationales linking each dialogue to corresponding alliance dimensions.
CARE is fine-tuned on the LLaMA-3.1-8BInstruct architecture. Experiments show that CARE
significantly bridges the gap where human counselors (who served as practitioners in these counseling sessions) in accurately gauging the therapeutic alliance from the client’s perspective, achieving over 70% higher Pearson correlation across
all dimensions. It also surpasses leading generalpurpose LLMs (e.g., GPT-4o and DeepSeek-R1)
across multiple metrics, including correlation, predictive precision, and stability. Further analyses
demonstrate that rationale-augmented supervision
provides additional gains beyond score-only finetuning, and replication on the Qwen2.5-7B model
confirms the robustness and generalizability of this
approach. Beyond predictive performance, CARE
generates high-quality, contextually grounded rationales that align closely with expert references while
reflecting human-like reasoning. Human evaluations further validate that these rationales are wellgrounded, dimension-specific, and informative.
We then apply the CARE model to a larger
dataset of real-world Chinese online counseling
1

Client-perceived Alliance Relationship Evaluator

conversations. The results reveal common challenges in alliance formation, demonstrate how
counselor-client interactions influenced the development of therapeutic alliance, and offer actionable
insights for optimizing intervention strategies, highlighting CARE’s potential as an AI-assisted tool
for supporting mental health care.
The primary contributions of this work are
summarized as follows:
(1) Dataset enrichment: We augment CounselingWAI with 9,516 expert-annotated rationales linking
conversational evidence to client alliance ratings.
(2) Rationale-augmented framework: We develop
CARE, an LLM-based model that predicts finegrained alliance dimensions while generating interpretable rationales.
(3) Empirical validation: CARE aligns closely
with client perceptions, outperforming human counselors and leading LLMs, with replication across
multiple architectures.
(4) Practical insights: CARE’s rationales reveal
common alliance-building challenges and patterns
in interactions, providing actionable guidance for
counseling practice.

2


## Related Work


Computational Alliance Assessment. A growing body of research has explored the use of NLP
techniques to assess the therapeutic alliance from
counseling conversations (Goldberg et al., 2020).
Early studies primarily adopted feature-based machine learning approaches, which represent entire
sessions using handcrafted linguistic or statistical
features and apply traditional classifiers to predict
a global alliance score (Goldberg et al., 2020; Ryu
et al., 2021; Martinez et al., 2019). While these
methods provide a estimation of relational quality,
they fail to capture the contextual dynamics and
interactive patterns that are central to the counselor–client relationship, and they overlook the
multidimensional components of the alliance.
Another line of work employed embeddingbased similarity approaches, where semantic
embeddings are computed for individual dialogue turns and compared with textual descriptions of questionnaire items to estimate alliance
strength (Lin et al., 2024, 2025). Although this
paradigm aligns model outputs with theoretical
constructs of alliance, it treats conversational turns
independently and neglects the global therapeutic
context. Moreover, the resulting scores are black-

---

box, offering limited transparency and explainability.
In contrast, our work proposes an explainable
computational framework that aligns closely with
client-perceived multidimensional alliance while
generating interpretable rationales grounded in
counseling dialogue.
LLMs in Mental Health Conversation Analysis. With the rise of LLMs’ advanced text understanding and reasoning capabilities, researchers
have increasingly turned to these models for mental health-related analysis based on conversational
data (Ji et al., 2023; Adhikary et al., 2024; Chiu
et al., 2024). Many studies focus on leveraging
LLMs to detect mental health conditions, such as
anxiety, depression and suicide ideation (Lamichhane, 2023; Yang et al., 2023; Xu et al., 2024; Yang
et al., 2023) and predict the Big Five personality
traits (Yan et al., 2024; Amin et al., 2023).
Some studies explore the use of LLMs to evaluate counseling conversations (Lee et al., 2024; Li
et al., 2024; Wang et al., 2024; Lin et al., 2025).
For example, Lee et al. (2024) use GPT models to
classify overall session quality as positive, neutral,
or negative, while others assess therapeutic alliance
through dialogue (Li et al., 2024; Wang et al., 2024).
Notably, Li et al. (2024) propose a prompting-based
framework with Chain-of-Thought reasoning to approximate expert-rated alliance. In contrast, we
model client-perceived alliance which is more directly linked to treatment outcomes, and move beyond prompting by adopting a rationale-augmented
supervision paradigm. By leveraging 9,516 expertcurated rationales, we fine-tune a specialized model
that internalizes domain knowledge rather than relying solely on general-purpose LLM capabilities.

3

Measurement of Therapeutic Alliance

The therapeutic alliance is broadly recognized as
a collaborative element of the client-counselor relationship (Bordin, 1979; Ardito and Rabellino,
2011). This multifaceted concept, which integrates
both cognitive and emotional interactions, is generally characterized by three components: (a) mutual agreement on the goals of therapy (Goal); (b)
a shared understanding that the therapeutic tasks
will effectively address clients’ specific concerns
(Task); and (c) the strength of the interpersonal
bond between clients and counselors (Bond) (Bordin, 1979). Each dimension captures a distinct yet
complementary aspect of the alliance, enabling a

comprehensive assessment of the therapeutic process.
In both clinical counseling and research, the
short revised Working Alliance Inventory (WAI)
is among the most widely used measures of these
three alliance dimension. The inventory is available in two versions—one for counselors and one
for clients—that are nearly identical, differing only
in the grammatical subject. It consists of 12 items,
with four items devoted to each dimension of the
therapeutic alliance. Each item is rated on a 5point Likert scale: 1 = Seldom; 2 = Sometimes; 3
= Fairly Often; 4 = Very Often; 5 = Always. Dimension scores are derived by averaging the four
items within each subscale. The reliability and validity of this inventory have been well-established
across various forms of psychotherapy (Hatcher
and Gillaspy, 2006; Munder et al., 2010).

4

Data Collection

4.1

Data Source

The counseling conversations and corresponding
therapeutic alliance scores used in this study are
drawn from the research-restricted CounselingWAI
dataset (Li et al., 2024). This corpus comprises textbased, 50-minute counseling sessions conducted
between professional counselors and real clients
on an online Chinese psycho-counseling platform.
Following each session, both clients and counselors
completed their respective versions of the short revised Working Alliance Inventory. For this study,
we used a subset comprising 793 counseling conversations from 82 clients, each paired with clientreported working alliance scores. Among these,
728 sessions also include counselor-reported alliance scores. The distributions of client ratings
across each alliance dimension are shown in Appendix A.
4.2

Rationale Augmentation

The original dataset contained client ratings of the
working alliance as numerical scores only (see
§4.1), which provided no explanation for the evaluations. To enrich this data with interpretative evidence, we engaged two licensed counseling experts who also serve as clinical supervisors skilled
in providing feedback and guidance to counselors.
Their task was to identify supporting evidence from
the counseling conversations for each of the 12
item–score pairs in the questionnaire.
Drawing on their counseling and supervision

---

expertise, the experts concluded that high-quality
rationales should combine a holistic, session-level
analysis of counselor–client interactions with turnlevel identification of critical exchanges that likely
influenced clients’ ratings. This integrated approach captures overall session dynamics while
reducing bias from overemphasizing isolated turns.
To facilitate rationale construction, we adopted a
model-in-the-loop strategy, which has been shown
to enhance annotation quality (Li et al., 2023b). In
our setup, GPT-4o was prompted to generate draft
rationales using counseling dialogues alongside
corresponding items and client-provided groundtruth ratings. These drafts were then reviewed and
refined by one of the expert annotators to ensure
both fidelity to the original dialogue and consistency with the clients’ perceived scores. For instance, when a client assigned a low rating to the
item "I have gained a clearer understanding of what
changes I can make" within the task-setting dimension, the finalized rationale read: "The client expressed confusion about communication difficulties, but the counselor primarily facilitated selfexpression without offering actionable suggestions.
The client explicitly remarked, I still don’t know
what to do; the counseling time was not worth the
cost." Through this process, we developed 9,516
explanations (793 dialogues × 12 items) for rationale augmentation.

mension’s rationales by computing the log odds
ratio with an informative Dirichlet prior (Monroe
et al., 2008), comparing all unigrams in the rationales of one dimension against the other two.
Rationales for each dimension were significantly
associated with specific key phrases (e.g., Goal
with "establish," Task with "method," Bond with
"support") (see Appendix A).

4.3

5.1

Data Quality

To ensure the quality of the generated rationales,
we implemented a cross-evaluation protocol in
which each expert assessed the complete set of
rationales corresponding to 100 counseling conversations authored by their counterpart. This process
yielded a total of 2,400 rationale evaluations, representing approximately 25% of the overall dataset.
The assessment was conducted using a 5-point Likert scale along three dimensions, with a score of
3 set as the acceptability threshold. The evaluation criteria comprised: (1) Faithfulness - how
accurately the rationale reflected both the dialogue
content and the client’s actual rating; (2) Relevance
- how directly the rationale addressed the specific
aspect being evaluated; and (3) Informativeness
- whether the rationale provided context-specific
rather than generic statements. Results demonstrated high quality across all aspects, with mean
scores of 4.820.39 for Faithfulness, 4.500.65 for Relevance, and 4.200.55 for Informativeness.
We further examine lexical patterns for each di-

4.4

Privacy and Ethics

All personal identifiers in the original CounselingWAI dialogue data have been thoroughly
anonymized to ensure participant privacy. In accordance with CounselingWAI’s data sharing policy,
the data will only be accessible to researchers who
have obtained proper authorization from CounselingWAI. This work is intended to serve as an auxiliary tool for counselors to better understand their
clients’ perception of the working alliance. Its outputs should be adopted with caution in practice and
do not provide any treatment recommendations or
diagnostic claims.

5

CARE Model

Leveraging the collected dataset, we developed
CARE, an automatic LLM-based model for predicting client-perceived working alliance scores
from text-based conversations, while simultaneously generating context-sensitive explanations.
Task Definition

Formally, we define the task of therapeutic relationship evaluation as follows: given a counseling
conversation and each corresponding measurement
item, the model predicts the client’s rating and identifies supporting evidence from the dialogue. For
each dimension, the predicted score is computed as
the average of the predicted ratings across its four
representative items. Model performance is then
evaluated per dimension by calculating the Pearson
correlation (r), Spearman correlation (ρ), and mean
squared error (MSE) with respect to the client’s
self-reported scores, following evaluation protocols widely adopted in prior work (Shick Tryon
et al., 2007; Bachelor and Salamé, 2000; Goldberg
et al., 2020; Lalk et al., 2024). For model-generated
rationales, we further assess their quality through
both automatic and human evaluations. Automatic
metrics include BLEU, ROUGE-1, ROUGE-L, and
BERTScore, which quantify textual similarity to
expert-written references. Additionally, human experts rate the rationales along three dimensions

---

Fold

#Client

#Session

Goal

Task

Bond

1
2
3
4
5
Total

15
16
16
18
17
82

147
154
157
171
164
793

3.741.07
3.711.12
4.150.81
4.110.93
3.691.05
3.891.02

3.521.15
3.511.06
3.970.86
3.870.98
3.361.10
3.651.06

3.741.06
4.050.91
4.310.80
4.220.87
3.990.93
4.070.93

Table 1: Summary statistics for each fold, including the
number of clients, number of sessions, and the mean
with standard deviation of goal, task, and bond scores.

(faithfulness, relevance, and informativeness, following the procedures described in § 4.3).
5.2

Data Preparation

To obtain robust performance estimates and reduce
bias from a single train–test split, we adopted a
5-fold cross-validation. The dataset was divided
into five mutually exclusive subsets, with stratified
sampling applied based on the score distributions
of the three working alliance dimensions. This ensured consistent score distributions across folds. To
prevent data leakage, all sessions from the same
client were assigned exclusively to either the training or validation set. This design minimizes the risk
of client-specific memorization and better reflects
real-world deployment, where the model must generalize to unseen clients.
As summarized in Table 1, we report for each
fold the number of counseling sessions and clients,
along with the mean and standard deviation of the
goal, task, and bond scores. During training, models were fine-tuned on four folds and validated on
the hold-out fold, with the optimal checkpoint selected based on Pearson correlation on the validation set. For prompt-based approaches, models
were directly applied to each validation fold. Final
performance is reported as the average and standard
deviation across all five folds.
5.3

Experimental Setup

We trained our CARE model using LLaMA-3.1-8BInstruct as the backbone, a widely adopted opensource instruction-tuned model chosen to balance
performance and deployment efficiency. Supervised full-parameter fine-tuning was conducted on
the training data for 10 epochs with a learning rate
of 5×10−7 and a fixed random seed of 123. During
inference, the temperature and nucleus sampling
parameters were set to 0 and 1.0, respectively, to
ensure deterministic outputs.

Model training was conducted using LLaMAFactory (Zheng et al., 2024), and all experiments
were run on eight NVIDIA A100 (80GB) GPUs.
Additional implementation details, including the
template prompt, are provided in Appendix C.1.
5.4

Baselines

To evaluate the performance of our proposed CARE
model in estimating clients’ perceived therapeutic
alliance, we compared it against several representative baselines, including human counselors and
large language models (LLMs).
Human Counselors. We incorporated the alliance
ratings provided by the counselors themselves, as
originally collected in the dataset (see §4.1). Human performance was computed across all 729 sessions for which both counselor and client alliance
ratings were available.
LLMs. We further examined the performance of
advanced open- and closed-source LLMs in a zeroshot setting. The closed-source models include
ChatGPT (OpenAI, 2023a), GPT-4o-mini (OpenAI,
2024), GPT-4o (OpenAI, 2023b), and Claude-3Sonnet (Anthropic, 2024). The open-source models
include the Qwen2.5-Instruct series (Yang et al.,
2024) (7B, 14B, 32B, and 72B), the LLaMA-3.1Instruct series (AI@Meta, 2024) (8B and 70B), and
DeepSeek-R1 (DeepSeek-AI, 2025).
5.5

Additional Experiments

Ablation Study on Augmented Rationales. To
examine the contribution of the augmented rationales to model performance, we conducted an ablation study in which the LLaMA-3.1-8B-Instruct
model was trained on the dataset containing only
client-provided ratings, with all rationale annotations removed.
Generalization Across Different Architectures.
To further assess the robustness and generalizability of the proposed dataset, we replicated the experiments using the Qwen2.5-7B-Instruct model,
following the same fine-tuning procedure as employed for our CARE model and its ablated variant.

6

Results and Analysis

6.1

Main Results

Table 2 presents the performance of different models across the three alliance dimensions, benchmarked against clients’ self-reported ratings under
all experimental settings. The comparison includes

---

Model Name
Human Counselor
GPT-3.5-Turbo
GPT-4o-mini
GPT-4o
Claude-3-Sonnet
DeepSeek-R1
Qwen2.5-7B-Instruct
Qwen2.5-14B-Instruct
Qwen2.5-32B-Instruct
Qwen2.5-72B-Instruct
Llama-3.1-8B-Instruct
Llama-3.1-70B-Instruct
CARE (Our Model)

Pearson↑
0.30
0.270.11
0.350.11
0.430.07
0.350.13
0.420.14
0.220.06
0.300.11
0.320.08
0.300.10
0.240.10
0.400.12
0.520.06

Goal
Spearman↑
0.27
0.240.11
0.310.12
0.400.09
0.360.13
0.390.14
0.210.05
0.280.11
0.300.09
0.290.09
0.240.10
0.380.12
0.500.07

MSE↓
1.36
2.100.37
1.270.19
2.030.40
2.090.39
2.360.55
2.630.26
2.170.22
2.510.33
1.950.22
2.980.54
2.200.42
1.000.16

Pearson↑
0.30
0.300.11
0.360.11
0.480.08
0.430.13
0.490.12
0.280.08
0.370.08
0.360.07
0.340.09
0.360.08
0.450.11
0.500.08

Task
Spearman↑
0.28
0.290.11
0.340.14
0.490.10
0.410.14
0.480.13
0.270.08
0.350.08
0.350.08
0.330.08
0.360.09
0.430.12
0.490.08

MSE↓
1.61
1.160.13
1.110.15
1.620.37
1.470.29
1.170.26
1.760.18
1.760.12
1.830.24
1.620.13
2.330.47
1.320.24
1.050.04

Pearson↑
0.22
0.300.09
0.340.12
0.370.15
0.290.10
0.400.17
0.250.12
0.300.08
0.270.09
0.270.10
0.260.14
0.330.11
0.460.05

Bond
Spearman↑
0.21
0.280.10
0.310.12
0.350.14
0.230.09
0.370.14
0.230.09
0.270.06
0.250.07
0.240.08
0.270.12
0.300.09
0.410.04

MSE↓
1.24
1.890.30
0.900.04
0.970.12
1.510.17
0.770.21
1.250.16
2.400.21
2.370.15
2.060.23
3.310.67
0.920.10
0.700.10

Human Automatic

Table 2: Performance of different models across the three alliance dimensions, including human counselors ratings,
baseline models, and the proposed CARE model, benchmarked against clients’ self-reported ratings. Evaluation
metrics include the Pearson’s r, Spearman’s ρ, and MSE. ↑/↓ indicates that higher/lower values are better. The best
results in each column are shown in bold.

Metrics
BLEU
ROUGE-1
ROUGE-L
BERTScore
Faithfulness
Relevance
Informativeness

Goal
0.220.01
0.560.00
0.420.00
0.790.00
4.770.08
4.500.12
4.340.09

Task
0.230.00
0.550.00
0.420.00
0.790.00
4.870.04
4.730.03
4.450.11

Bond
0.280.01
0.570.01
0.470.01
0.810.00
4.810.07
4.780.11
4.270.10

Table 3: Comparison of CARE-generated rationales
and expert-written rationales in terms of automatic
evaluation metrics (BLEU, ROUGE-1, ROUGE-L, and
BERTScore) and human assessment dimensions (Faithfulness, Relevance, and Informativeness).

ratings from human counselors, all baseline models, and our proposed CARE model. From these
results, we have several findings:
CARE significantly bridges the gap where human counselors may struggle to accurately
gauge the therapeutic alliance from the client’s
perspective. Human counselors exhibited only
moderate alignment with client self-reports, with
Pearson correlations ranging from 0.22 to 0.30
across the Goal, Task, and Bond dimensions. This
is consistent with prior findings that counselors
often struggle to accurately assess the counseling
quality from their clients’ perspectives (Hatcher
et al., 1995; Shick Tryon et al., 2007), highlighting
the inherent difficulty of this task. In contrast, the
CARE model achieved substantially higher correlations of 0.52 (Goal), 0.50 (Task), and 0.46 (Bond),
corresponding to improvements of approximately
73%, 67%, and 109% in Pearson correlation for the
respective dimensions.
These results suggest that the CARE model

could serve as a reliable tool for providing quantitative feedback to counselors, helping them better
calibrate their perception of the therapeutic alliance
against clients’ reported experiences.
CARE outperforms even the most powerful
general-purpose LLMs in correlation, predictive precision, and stability. Among zero-shot
prompting models, GPT-4o and DeepSeek-R1 exhibited the strongest performance. Compared to
these top competitors, CARE consistently outperformed across all three alliance dimensions, with
notable gains on the Goal and Bond dimensions.
Specifically, CARE improved Pearson and Spearman correlations by 21% and 25% on the Goal
dimension, and by 15% and 11% on the Bond dimension.
In terms of predictive precision, CARE achieved
the lowest MSE values across all three dimensions
(Goal: 1.00, Task: 1.05, Bond: 0.70). On the
Goal dimension, CARE’s MSE was 51% lower
than GPT-4o (2.03) and 58% lower than DeepSeekR1 (2.36), indicating that its predictions were not
only highly correlated with client ratings but also
numerically closer to the ground-truth scores. Furthermore, CARE exhibited remarkably low standard deviations compared to the top competitors,
ensuring stable and reliable performance in realworld applications.
Beyond predictive metrics, the rationales generated by CARE also show high semantic alignment with expert-written references, despite lexical
variations (see Table 3). This finding reflects the
model’s ability to construct human-like reasoning
chains from dialogue rather than merely replicating reference expressions. Human evaluation fur-

---

Architectures
Qwen2.5-7B-Instruct
Llama-3.1-8B-Instruct

Rationale
×
✓
×
✓

Pearson↑
0.370.12
0.420.08
0.450.09
0.520.06

Goal
Spearman↑
0.360.14
0.400.10
0.430.11
0.500.07

MSE↓
1.550.20
1.490.17
1.100.14
1.000.16

Pearson↑
0.380.13
0.410.09
0.450.11
0.500.08

Task
Spearman↑
0.370.13
0.410.11
0.440.10
0.490.08

MSE↓
1.600.17
1.580.10
1.180.11
1.050.04

Pearson↑
0.340.12
0.360.09
0.440.07
0.460.05

Bond
Spearman↑
0.310.09
0.330.06
0.390.07
0.410.04

MSE↓
1.440.25
1.370.24
0.920.17
0.700.10

Table 4: Results of generalization and ablation studies for fine-tuning with versus without rationales, using Qwen2.57B-Instruct and LLaMA-3.1-8B-Instruct as backbones. Evaluation metrics include the Pearson’s r, Spearman’s ρ,
and MSE. ↑/↓ indicates that higher/lower values are better. The best results in each column are shown in bold.

ther confirms the quality of generated rationales,
demonstrating strong grounding in session content,
accurate focus on dimension-specific cues and adequate coverage of contextual information.
CARE transformed its backbone into a highly
accurate, stable, and reliable model in predicting therapeutic alliance. The backbone of
CARE, LLaMA-3.1-8B-Instruct, showed relatively
poor performance under zero-shot prompting, with
correlations as low as 0.24 (Goal) and 0.26 (Bond),
and MSE values exceeding 2 across dimensions.
After fine-tuning on our proposed dataset, CARE
achieved substantial improvements, corresponding
to 117%, 47%, and 77% increases in Pearson correlation on the Goal, Task, and Bond dimensions, respectively. MSE values dropped to approximately
1 across all dimensions, with the Bond dimension
decreasing from 3.31 to 0.70 (a 79% reduction).
Furthermore, the high standard deviations of the
base model were drastically reduced, demonstrating that fine-tuning specialized the model for this
task, yielding consistent and reliable predictions.
6.2

Additional Results

Table 4 summarizes the ablation study evaluating
the effect of rationale augmentation and its generalizability across model architectures.
Rationale-augmented supervision enhanced
CARE’s predictive capability. Fine-tuning the
CARE model with rationale-augmented supervision yielded consistent and significant gains
across all therapeutic alliance dimensions compared to training without rationales. Correlation
metrics improved notably—by approximately 16%
on the Goal dimension and 11% on the Task
dimension—while predictive errors (MSE) were
markedly reduced, exemplified by a reduction from
0.92 to 0.70 on the Bond dimension. These results highlight the efficacy of incorporating expertgenerated textual rationales during training, enabling the model to internalize human evaluative

reasoning and attend to high-quality cues for more
reliable alliance assessment.
CARE’s rationale-augmented training generalized across model architectures. Consistent
with the findings on LLaMA-3.1-8B-Instruct, the
Qwen2.5-7B-Instruct model exhibited a similar performance pattern, showing a substantial improvement from score-based fine-tuning, followed by further gains with rationale-augmented training. This
consistency demonstrates that the benefits of rationale supervision are architecture-agnostic, validating the robustness and high quality of our proposed
dataset.
6.3

Case Study

To better understand the limitations of the CARE
model, we examined cases where its predictions deviated from client-reported ratings (see Table 6) and
analyzed model-generated explanations to identify
the underlying causes.
Our analysis revealed that the model tends to prioritize verbal content while overlooking important
behavioral cues. For instance, in the first case, the
client arrived late and departed early, suggesting
limited respect and weak emotional engagement.
However, the model focused exclusively on the
superficially polite language and inferred a high
level of respect. Moreover, the model may overemphasize some positive or negative statements while
neglecting the broader contextual dynamics. In the
second case, although the client initially acknowledged the benefits of previous counseling, they
later provided minimal responses and disengaged
from session activities. Yet, the model weighted
the positive statements disproportionately, failing
to capture the deteriorating therapeutic alliance.
These findings align closely with insights emphasized by experts during our rationale augmentation
process—that accurate assessment of therapeutic
alliance requires integrative analysis of both specific verbal exchanges and the overall interaction
pattern. Enhancing this integrative reasoning capa-

---

4.5

Goal
4.03

4.0

3.90

3.72

3.5

Bond

Task

3.62

3.50

3.88
3.60

3.57
3.34

3.26
3.07

3.0

2.5

3.84

Counselor A
(288 Sessions)

Counselor B
(203 Sessions)

Counselor C
(165 Sessions)

Figure 2: Working alliance scores by dimension for
the three most active counselors; dashed lines indicate
overall counselor averages.

bility represents a crucial direction for future model
refinement.

7

Insights based on LLM Predictions

We use the CARE model to explore therapeutic alliance in text-based psychological counseling. This
model predicted client-perceived alliance across
2,236 sessions from the ClientBehavior dataset (Li
et al., 2023a), including a subset of 300 sessions
annotated with utterance-level counselor strategies
and client reactions. Our analysis examines counselors’ varying abilities to build alliances, how interaction patterns influence alliance development,
and actionable directions for improving practice.
Counselors’ Varying Abilities. Overall, counselors formed a generally solid therapeutic alliance,
though substantial room for improvement remains
(see Figure 2). Collaboration on counseling tasks,
a core mechanism for behavioral change, emerged
as the weakest dimension.
Analysis of the three counselors with the highest session volumes (≥165 sessions) revealed distinct alliance profiles. Counselor B scored below
the overall mean across all dimensions, indicating
ongoing difficulties in aligning with clients, especially on goals and tasks. In contrast, Counselor A
showed excelled in building emotional trust (bond
> 4), whereas Counselor C performed best in establishing shared goals. Since these dimensions
ideally develop together (Bordin, 1979), these patterns highlight the need for counselors to improve
their weaker areas.
Interaction Patterns Affecting Alliance. We analyzed micro-level interaction patterns in the 300
annotated sessions using multiple regression, with

counselor–client patterns as predictors and sessionlevel alliance scores as outcomes.
Across all dimensions, the combination of counselor Supporting strategies and clients’ Negative
responses was linked to lower alliance scores,
strongest for the bond dimension (β = 6.36, p <
0.001). In contrast, counselor Challenging strategies paired with clients’ Positive responses predicted higher alliance scores, particularly on the
task dimension (β = 2.64, p < 0.001). These findings underscore the bidirectional nature of counseling interactions and the importance of adapt strategies in response to client feedback to strengthen
the alliance.
Actionable Insights for Counselors. Focusing
on Counselor B, who struggled to establish strong
alliances, model explanations for sessions with low
alliance scores (≤2) revealed clear interaction patterns.
The counselor often struggled to set concrete
goals with clients, with discussions drifting into
open-ended exploration. Counseling activities (e.g.,
overuse of "mm-hmm" responses) were misaligned
with goals, and suggestions were vague and not actionable. Responses appeared mechanical, empathy
was limited, and attempts to repair the relationship
were largely ineffective when clients expressed dissatisfaction. These observations suggest that Counselor B would benefit from improving goal clarity,
aligning tasks with goals, and providing more responsive emotional feedback.
Building on these insights, we aim to integrate
LLM-based real-time evaluation and feedback into
counseling practice to support counselors in cultivating deeper connections with their clients in
future work.

8


## Conclusion


We augment counseling dialogues with expertcurated rationales aligned with client-reported
working alliance scores and introduce a novel LLM
framework for assessing multidimensional therapeutic alliance with interpretable evidence. Experiments show that a smaller fine-tuned LLM
with rationale-based supervision aligns with client
perceptions more closely than both human counselors and larger general-purpose LLMs. Moreover,
CARE demonstrates its potential as an AI-assisted
tool for supporting text-based mental health care.
Data, code, and models are available at this URL.

---


## References

Prottay Kumar Adhikary, Aseem Srivastava, Shivani Kumar, Salam Michael Singh, Puneet Manuja,
Jini K Gopinath, Vijay Krishnan, Swati Kedia,
Koushik Sinha Deb, and Tanmoy Chakraborty. 2024.
Exploring the efficacy of large language models in
summarizing mental health counseling sessions: A
benchmark study. Preprint, arXiv:2402.19052.
AI@Meta. 2024. Llama 3 model card.
Mostafa M Amin, Erik Cambria, and Björn W Schuller.
2023. Will affective computing emerge from foundation models and general artificial intelligence? a
first evaluation of chatgpt. IEEE Intelligent Systems,
38(2):15–23.

Adam O Horvath, AC Del Re, Christoph Flückiger,
and Dianne Symonds. 2011. Alliance in individual
psychotherapy. Psychotherapy, 48(1):9.
Adam O Horvath and Lester Luborsky. 1993. The role
of the therapeutic alliance in psychotherapy. Journal
of consulting and clinical psychology, 61(4):561.
Adam O Horvath and B Dianne Symonds. 1991. Relation between working alliance and outcome in psychotherapy: A meta-analysis. Journal of counseling
psychology, 38(2):139.
Shaoxiong Ji, Tianlin Zhang, Kailai Yang, Sophia Ananiadou, and Erik Cambria. 2023. Rethinking large
language models in mental health applications. arXiv
preprint arXiv:2311.11267.

Rita B Ardito and Daniela Rabellino. 2011. Therapeutic
alliance and outcome of psychotherapy: historical
excursus, measurements, and prospects for research.
Frontiers in psychology, 2:270.

Christopher Lalk, Tobias Steinbrenner, Weronika Kania, Alexander Popko, Robin Wester, Jana Schaffrath, Steffen Eberhardt, Brian Schwartz, Wolfgang
Lutz, and Julian Rubel. 2024. Measuring alliance and
symptom severity in psychotherapy transcripts using
bert topic modeling. Administration and Policy in
Mental Health and Mental Health Services Research,
51:1–16.

Alexandra Bachelor and Ramzi Salamé. 2000. Participants’ perceptions of dimensions of the therapeutic
alliance over the course of therapy. The Journal of
psychotherapy practice and research, 9(1):39.

Michael J Lambert and Dean E Barley. 2001. Research summary on the therapeutic relationship and
psychotherapy outcome. Psychotherapy: Theory,
research, practice, training, 38(4):357.

Anthropic. 2024. The claude 3 model family: Opus, sonnet, haiku. https://api.semanticscholar.org/
CorpusID:268232499. [Accessed 16-04-2024].

Edward S Bordin. 1979. The generalizability of
the psychoanalytic concept of the working alliance. Psychotherapy: Theory, research & practice,
16(3):252.
Yu Ying Chiu, Ashish Sharma, Inna Wanyin Lin, and
Tim Althoff. 2024. A computational framework for
behavioral assessment of llm therapists. Preprint,
arXiv:2401.00820.
DeepSeek-AI. 2025. Deepseek-r1: Incentivizing reasoning capability in llms via reinforcement learning.
Preprint, arXiv:2501.12948.
Simon B Goldberg, Nikolaos Flemotomos, Victor R
Martinez, Michael J Tanana, Patty B Kuo, Brian T
Pace, Jennifer L Villatte, Panayiotis G Georgiou, Jake
Van Epps, Zac E Imel, and 1 others. 2020. Machine learning and natural language processing in
psychotherapy research: Alliance as example use
case. Journal of counseling psychology, 67(4):438.
Robert L Hatcher, Alex Barends, James Hansell, and
M Janice Gutfreund. 1995. Patients’ and therapists’
shared and unique views of the therapeutic alliance:
an investigation using confirmatory factor analysis in
a nested design. Journal of Consulting and Clinical
Psychology, 63(4):636.
Robert L Hatcher and J Arthur Gillaspy. 2006. Development and validation of a revised short version of the
working alliance inventory. Psychotherapy research,
16(1):12–25.

Bishal Lamichhane. 2023. Evaluation of chatgpt for
nlp-based mental health applications. arXiv preprint
arXiv:2303.15727.
Younghun Lee, Dan Goldwasser, and Laura Schwab
Reese. 2024. Towards understanding counseling
conversations: Domain knowledge and large language models. In Findings of the Association
for Computational Linguistics: EACL 2024, pages
2032–2047, St. Julian’s, Malta. Association for Computational Linguistics.
Anqi Li, Yu Lu, Nirui Song, Shuai Zhang, Lizhi Ma,
and Zhenzhong Lan. 2024. Automatic evaluation for
mental health counseling using llms. arXiv preprint
arXiv:2402.11958.
Anqi Li, Lizhi Ma, Yaling Mei, Hongliang He,
Shuai Zhang, Huachuan Qiu, and Zhenzhong Lan.
2023a.
Understanding client reactions in online mental health counseling. In Proceedings
of the 61st Annual Meeting of the Association
for Computational Linguistics (Volume 1: Long
Papers), pages 10358–10376, Toronto, Canada. Association for Computational Linguistics.
Minzhi Li, Taiwei Shi, Caleb Ziems, Min-Yen Kan,
Nancy Chen, Zhengyuan Liu, and Diyi Yang.
2023b. CoAnnotating: Uncertainty-guided work allocation between human and large language models for data annotation. In Proceedings of the

## 2023 Conference on Empirical Methods in Natural

Language Processing, pages 1487–1505, Singapore.
Association for Computational Linguistics.

---

Baihan Lin, Djallel Bouneffouf, Yulia Landa, Rachel
Jespersen, Cheryl Corcoran, and Guillermo Cecchi.
2025. Compass: Computational mapping of patienttherapist alliance strategies with language modeling.
Translational Psychiatry, 15(1):166.

Georgiana Shick Tryon, Sasha Collins Blackwell,
and Elizabeth Felleman Hammel. 2007. A metaanalytic examination of client–therapist perspectives
of the working alliance. Psychotherapy research,
17(6):629–642.

Baihan Lin, Guillermo Cecchi, and Djallel Bouneffouf.
2023. Deep annotation of therapeutic working alliance in psychotherapy. In International workshop
on health intelligence, pages 193–207. Springer.

Georgiana Shick Tryon, Sasha Collins Blackwell, and
Elizabeth Felleman Hammel. 2008. The magnitude of client and therapist working alliance ratings. Psychotherapy: Theory, Research, Practice,
Training, 45(4):546.

Baihan Lin, Guillermo Cecchi, and Djallel Bouneffouf. 2024. Working alliance transformer for psychotherapy dialogue classification. In Proceedings
of the 6th Clinical Natural Language Processing
Workshop, pages 64–69, Mexico City, Mexico. Association for Computational Linguistics.

Jiashuo Wang, Yang Xiao, Yanran Li, Changhe
Song, Chunpu Xu, Chenhao Tan, and Wenjie Li.
2024. Towards a client-centered assessment of
llm therapists by client simulation. arXiv preprint
arXiv:2406.12266.

Daniel J Martin, John P Garske, and M Katherine
Davis. 2000. Relation of the therapeutic alliance
with outcome and other variables: a meta-analytic review. Journal of consulting and clinical psychology,
68(3):438.

Xuhai Xu, Bingsheng Yao, Yuanzhe Dong, Saadia
Gabriel, Hong Yu, James Hendler, Marzyeh Ghassemi, Anind K. Dey, and Dakuo Wang. 2024. Mentalllm: Leveraging large language models for mental
health prediction via online text data. Proc. ACM
Interact. Mob. Wearable Ubiquitous Technol., 8(1).

Victor R Martinez, Nikolaos Flemotomos, Victor
Ardulov, Krishna Somandepalli, Simon B Goldberg, Zac E Imel, David C Atkins, and Shrikanth
Narayanan. 2019. Identifying therapist and client
personae for therapeutic alliance estimation. In
Interspeech, volume 2019, page 1901. NIH Public
Access.
Burt L Monroe, Michael P Colaresi, and Kevin M Quinn.
2008. Fightin’words: Lexical feature selection and
evaluation for identifying the content of political conflict. Political Analysis, 16(4):372–403.
Thomas Munder, Fabian Wilmers, Rainer Leonhart,
Hans Wolfgang Linster, and Jürgen Barth. 2010.
Working alliance inventory-short revised (wai-sr):
psychometric properties in outpatients and inpatients.
Clinical Psychology & Psychotherapy:
An International Journal of Theory & Practice,
17(3):231–239.
OpenAI. 2023a. Chatgpt.
OpenAI. 2023b. Gpt-4 technical report. arXiv preprint
arXiv:2303.08774.
OpenAI. 2024. Gpt-4o mini: advancing cost-efficient
intelligence.
William E Piper, Hassan FA Azim, Anthony S Joyce,
and Mary McCallum. 1991. Transference interpretations, therapeutic alliance, and outcome in shortterm individual psychotherapy. Archives of general
Psychiatry, 48(10):946–953.
Jihan Ryu, Stephen Heisig, Caroline McLaughlin, Rebeccah Bortz, Michael Katz, and Xiaosi Gu. 2021.
A natural language processing approach to modelling treatment alliance in psychotherapy transcripts.
BJPsych Open, 7(S1):S48–S48.

Yang Yan, Lizhi Ma, Anqi Li, Jingsong Ma, and Zhenzhong Lan. 2024. Predicting the big five personality
traits in chinese counselling dialogues using large
language models. Preprint, arXiv:2406.17287.
An Yang, Baosong Yang, Beichen Zhang, Binyuan Hui,
Bo Zheng, Bowen Yu, Chengyuan Li, Dayiheng Liu,
Fei Huang, Haoran Wei, Huan Lin, Jian Yang, Jianhong Tu, Jianwei Zhang, Jianxin Yang, Jiaxi Yang,
Jingren Zhou, Junyang Lin, Kai Dang, and 22 others. 2024. Qwen2.5 technical report. arXiv preprint
arXiv:2412.15115.
Kailai Yang, Shaoxiong Ji, Tianlin Zhang, Qianqian
Xie, Ziyan Kuang, and Sophia Ananiadou. 2023. Towards interpretable mental health analysis with large
language models. Preprint, arXiv:2304.03347.
Yaowei Zheng, Richong Zhang, Junhao Zhang, Yanhan
Ye, Zheyan Luo, and Yongqiang Ma. 2024. Llamafactory: Unified efficient fine-tuning of 100+ language
models. arXiv preprint arXiv:2403.13372.

A

Data Analysis

Figure 3 shows the score distribution of the CounselingWAI dataset. The score distributions across
the three dimensions exhibit a typical negative
skew, a pattern commonly observed in real-world
alliance assessments (Tryon et al., 2008; Goldberg
et al., 2020). This characteristic indicates that the
dataset used for subsequent model training and evaluation reflects authentic client rating patterns. The
average scores for the Goal, Task and Bond dimensions all surpass 3.5, suggesting that a relatively
robust therapeutic relationship can be established
between counselors and clients in online text-based
psychological counseling.

---

B



























Figure 3: Distributions of client ratings across the
three working alliance dimensions—Goal, Task, and
Bond—illustrated using histograms, box plots, and halfviolin plots. Within each box, the X denotes the mean.
The central line represents the median, the box corresponds to the interquartile range (IQR, 25th–75th percentile), and the whiskers extend to the full range of the
data.

Dim

Length

Lexical Features

Goal

156.7113.66

目标/goal (55.32), 努力/effort (29.31),
探讨/explore (27.57), 改善/improve (24.97),
制定/establish (24.38)

Task

151.7612.80

方法/method (41.73), 意识/aware (40.05),
新/new (37.80), 改变/change (29.41)
解决问题/problem-solving (29.70)

Bond

157.2913.54

支持/support (45.51), 关心/care (38.76),
表现/express (37.59), 感受/feeling (37.05),
理解/understand (36.54)

Table 5: Data characteristics of generated rationales for
each working alliance dimension, including the mean
with standard deviation of rationale length and key lexical features. The rightmost column presents the five
words most strongly associated with each dimension’s
rationales, with rounded z-scored log-odds ratios provided in parentheses.

In addition, we analyzed the crafted rationales.
The generated rationales had an overall average
length of 155.25 characters, with a standard deviation of 13.27. To examine lexical patterns, we
extracted features for each dimension’s rationales
by computing the log odds ratio with an informative
Dirichlet prior (Monroe et al., 2008), comparing
all unigrams in the rationales of one dimension
against the other two. The top five phrases for each
dimension are presented in Table 5. Rationales
for each dimension were significantly associated
(z-score > 3) with specific key phrases (e.g., Goal
with "establish," Task with "method," Bond with
"support").

Background of Therapeutic Alliance

The therapeutic alliance is widely recognized
as a foundational construct in psychotherapy
and is commonly conceptualized as comprising
three interrelated components: Goal, Task, and
Bond (Bordin, 1979).
Goal. Establishing clear counseling goals is fundamental to a successful counseling session, distinguishing it from casual conversations. Therapeutic
goals involve fostering positive changes in clients’
thoughts, cognition, and behaviors, facilitated by
counselors’ guidance and support. Both counselors
and clients should collaboratively define and mutually agree on their counseling goals, ensuring their
efforts are directed toward shared objectives.
Task. Beyond setting consistent goals, reaching
mutual agreement between counselors and clients
on specific methods to achieve them is a critical
element. Counselors typically propose tasks based
on their personal styles, experience, and predispositions, but clients may find them unmanageable
or unsuitable. In such instances, counselors need
to provide alternative approaches to better engage
their clients. Furthermore, counselors should clarify how these tasks contribute to achieving therapy
goals, as this understanding is crucial for effective
treatment (Horvath and Luborsky, 1993).
Bond. In addition to the cognitive aspects of the
alliance that emphasize the consensus on therapy
goals and tasks, the emotional attachment between
counselors and clients is crucial. The bond reflects
the feelings and attitudes that each party holds toward the other, fostering collaboration and trust.
When clients perceive counselors’ genuine care
and attention, they feel secure and motivated to
engage in therapy. Likewise, when both parties
trust each other’s abilities, a shared commitment to
goals and tasks can be established.

C

Automatic Prediction

C.1

Template Prompt

The template prompt used to instruct LLMs to predict clients’ perceived working alliance is shown
in Figure 4.
C.2

Experimental Settings

Table 7 shows the key hyperparameters and corresponding values used in our fine-tuning experiments.

---

Here is the psychological counseling dialogue between you as a client and
your counselor.
Counselor: Hi, what would you like to talk about today?
Client: Recently, I often use sleep to escape from facing life.
Counselor: I see. What do you feel you‘re trying to escape from?
Client: Things I can’t control, but that are still my own.
…
Before the end of this psychological counseling session, please complete the
following multiple-choice question based on the conversation and your own
situation. Provide the corresponding reasons with direct quotes from the
dialogue between you and the counselor. (Output should be two lines, with
each line indicating the choice and reason respectively):
Question: I feel that the things I do in therapy will help me to accomplish
the changes that I want.
Options: 1. Seldom; 2. Sometimes; 3. Fairly Often; 4. Very often; 5. Always

Figure 4: The template prompt for instructing LLMs
to predict clients’ perceived working alliance, using
an example conversation and questionnaire question
(displayed in cadetblue italic text).

C.3

Experimental Results

Table 6 presents the example cases where the
model’s predictions significantly deviate from the
client’s self-reported scores.

D

Additional LLM-based Insights

D.1

Interaction Patterns and Therapeutic
Alliance

Table 8 shows the regression coefficients for counselor–client interaction patterns predicting sessionlevel working alliance scores across the three dimensions.
D.2

Example Explanations

Table 9 presents some example explanations generated by our best-performing model.

E

Limitations

First, while our approach is validated on text-based
counseling, its principles are applicable to other
modalities (e.g., face-to-face or video sessions)
through speech-to-text conversion. Future work
could extend this by integrating multi-modal signals such as vocal tone and facial expressions.
Second, although the data comes from a single
Chinese platform, the underlying mechanisms of
therapeutic alliance are largely universal, and our
diverse dataset supports cross-context generalizability. Future efforts will test and adapt the model
across languages and cultures through fine-tuning
and expanded data collection. Additionally, the
lack of strictly longitudinal data limits our ability
to assess temporal dynamics, a direction we plan
to address in subsequent studies.

Third, the rationales used to augment dialogues
are derived from expert annotations rather than
client self-reports, given the practical challenges in
obtaining scalable first-person explanations. While
this aligns with clinical supervision practices, it
may introduce professional bias, meaning the
model learns expert inference patterns rather than
client-internal reasoning. Future work should explore hybrid approaches combining expert and
client perspectives.
Finally, there remains room to improve the
model’s correlation with client ratings and the precision of rationale generation. We will refine training strategies, optimize instructions, and expand
datasets to enhance performance and robustness.
Despite these limitations, this work offers meaningful insights into the integration of NLP and psychological process research.

F

Human Data Collection

The newly collected human data in this study consist of expert-authored explanatory rationales augmenting pairs of original counseling dialogues and
corresponding client-rated working alliance inventory items.
(1) For each dialogue, experts were provided
with the full transcript, the relevant working alliance item, and the client’s rating. Drawing on
their clinical and supervisory expertise, they identified evidence from the dialogue and synthesized it
into a structured rationale explicitly linking textual
evidence to the alliance score.
(2) Experts were recruited from universities and
professional institutions. All held valid counseling
licenses and possessed formal supervisory qualifications and substantial practice experience. Each
expert received approximately 10k RMB as compensation for their annotation work.
(3) All participants provided written informed
consent prior to participation. They were fully informed of the study procedures, research objectives,
data usage policies, and their right to withdraw at
any time without penalty.
(4) This study was reviewed and approved by
the appropriate Institutional Review Board (IRB).

G

Ethics Statement

Data Privacy and Release. The original counseling dataset is fully anonymized and released under
strictly controlled research conditions. Access requires a formal application process, which includes

---

Conversation
Counselor: Hello, are you online?
10 minutes later...
Client: Sorry, I fell asleep.
Counselor: It’s okay, let’s begin now.
Client: Thanks for waiting for me.
Counseling in progress...
Counselor: Do you have any plans for progress?
Counselor: Are you still online? Hello?
Counseling in progress...
Client: I’ve been doing counseling for a while,
and slowly I’ve started to shift my focus. I’m feeling
a bit better now.
Counseling in progress...
Counselor: You don’t want to have a negative
impact on her?
Client: Yes.
Counselor: You don’t want to put her in a difficult position?
Client: I guess so.
Counseling in progress...

Evaluation Results
Dimension: Bond
Client: 1.25
CARE: 4.25
Explanations: The counselor patiently waits for
the client’s responses, even when the client falls
asleep, without showing any impatience. The
client also responds in a friendly manner, such as
saying "Sorry" and "Thanks". These interactions
reflect mutual respect and understanding...

Dimension: Task
Client: 1.0
CARE: 4.0
Explanations: The client directly stated that
counseling has helped them clarify the areas
that need change, and feel better by shifting
focus...

Table 6: Example cases where the model’s predictions significantly deviate from the client’s self-reported scores.

Hyperparameters
Per-device Train Batchsize
Gradient Accumulation Steps
Warmup Ratio
LR Scheduler Type
Learning Rate
Data Type
Optimizer
Epoch

Value
1
2
0.1
cosine
5e-7
bfloat16
adamw
10

Table 7: The hyperparameters with values used in our
fine-tuning experiments.

Supporting - Positive
Challenging - Positive
Supporting - Negative
Challenging - Negative

Goal

Task

Bond

0.17
2.07***
-5.71***
-1.70

0.84
2.64***
-5.57***
-2.74

0.62
1.47***
-6.36***
-1.77

Table 8: Regression coefficients for counselor–client
interaction patterns predicting session-level working
alliance scores across the three dimensions; *** denotes
p < 0.001.

submission of valid identification, a detailed research justification, proof of full-time academic
affiliation, and documented IRB approval from the
applicant’s institution. Only full-time principal
investigators are eligible to apply, and each application is subject to review by the applicant’s Office
of Research. Approved applicants must also sign a
legally binding Data Non-Disclosure Agreement,
committing not to share the data with any third
party. The augmented dataset is available under
identical terms, and eligibility is contingent upon
prior access to the original dataset.
LLM-based Predictions. This study aims to
introduce an automated approach for predicting
client-rated therapeutic alliance with their counselors in the context of online text-based counseling. We advocate for using LLM-based predictions as an additional tool to help counselors gain
a deeper understanding of their clients. It is not
designed for clinical diagnosis, therapeutic intervention, or as a replacement for professional clinical judgment. Given the inherent limitations of
current LLMs, predictions should be interpreted
with caution. Furthermore, we highlight the importance of considering broader societal and ethical
implications, including safeguards against potential misuse, when implementing such technology
in sensitive domains.

---

Dimension

Goal

Evaluation

bad

good

Approach

bad

good

Bond

bad

good

Example
In our conversations, although the counselor tried to guide me in exploring issues
and feelings, we did not clearly agree on specific areas for change. For example,
when I mentioned how to deal with a difficult roommate, the counselor focused
more on understanding my feelings and situation rather than collaboratively
determining specific change strategies. My responses, such as “No thanks” and
later mentioning “I might not be suited for this,” indicate that my understanding of
the counseling process may differ from the counselor’s expectations. As a result,
we rarely reached a consensus on the areas where I needed to make efforts for
change.
In the conversation, the counselor and I jointly established counseling goals, such
as, “Let’s set the goal to increase daily sleep time to 6 hours.” This indicates that
we were indeed actively involved in the goal-setting process, which was a
continuous part of the counseling sessions, thus aligning with the description of
“always” collaboratively setting goals.
In the conversation, I expressed my feelings about the counselor’s questions,
saying, “To be honest, I speak directly and bluntly, and this is a free service. I
shouldn’t have any expectations. I really shouldn’t have too many demands and
should be content.” This indicates that I did not feel the counseling provided new
perspectives or methods for addressing my relationship issues. The counselor
focused more on listening and understanding, whereas I was expecting concrete
guidance and solutions, such as, “Shouldn’t you be better and have more ideas?”
This shows that I didn’t frequently find new ways to view my problems during the
counseling sessions.
In the conversation, I mentioned trying to make changes but not finding the right
approach, which indicates that I recognize the value of the counseling process. The
counselor helped me reflect on my concerns about effort and boundaries, for
example, “It seems like you feel that the evaluation of your goodness comes from
what you do rather than your traits or personal charisma in relationships.” This
helped me start to understand my behavioral patterns more deeply. Although I am
still exploring, I feel that counseling has indeed guided me toward the changes I
want.
In the conversation, I expressed doubts about the counselor’s professionalism and
mentioned, “You gave me the impression of being a bit rushed, not allowing me time
to process my changes,” as well as “I have a lot of anger towards you.” This
indicates that I did not feel that the counselor was attuned to my personal
preferences but rather sensed a mismatch in professional approach.
During the counseling process, the counselor demonstrated patience and
understanding, such as by asking, “Can you describe the sense of presence you
have experienced from childhood to now?” This indicates that the counselor
actively listens and is concerned about my feelings. Although personal preferences
were not directly addressed, the counselor’s positive feedback and in-depth
exploration, such as, “The sense of presence you described—when you feel that
doing something genuinely brings joy to others—seems to be part of your value
system. It looks like you have a direction, but the path is blocked,” show the
counselor’s deep understanding and care for me, making me feel valued and
supported.

Table 9: Example explanations generated by our best-performing model.

---
