arXiv:2406.16478v1 [cs.CL] 24 Jun 2024

EMMI - Empathic Multimodal Motivational
Interviews Dataset: Analyses and Annotations
Lucie Galland

Catherine Pelachaud

Florian Pecune

ISIR
Sorbonne university
Paris, France
lucie.galland@isir.upmc.fr

CNRS, ISIR
Sorbonne university
Paris, France
catherine.pelachaud@isir.upmc.fr

CNRS - SANPSY,
Bordeaux University
Bordeaux, France
florian.pecune@u-bordeaux.fr

Abstract—The study of multimodal interaction in therapy can
yield a comprehensive understanding of therapist and patient
behavior that can be used to develop a multimodal virtual
agent supporting therapy. This investigation aims to uncover how
therapists skillfully blend therapy’s task goal (employing classical
steps of Motivational Interviewing) with the social goal (building
a trusting relationship and expressing empathy). Furthermore, we
seek to categorize patients into various “types” requiring tailored
therapeutic approaches. To this intent, we present multimodal
annotations of a corpus consisting of simulated motivational
interviewing conversations, wherein actors portray the roles of
patients and therapists. We introduce EMMI, composed of two
publicly available MI corpora, AnnoMI and the Motivational
Interviewing Dataset, for which we add multimodal annotations.
We analyze these annotations to characterize functional behavior
for developing a virtual agent performing motivational interviews
emphasizing social and empathic behaviors. Our analysis found
three clusters of patients expressing significant differences in
behavior and adaptation of the therapist’s behavior to those
types. This shows the importance of a therapist being able to
adapt their behavior depending on the current situation within
the dialog and the type of user.
Index Terms—Motivational Interviewing, Multimodal behaviors, Empathic behaviors

I. I NTRODUCTION
The prevalence of mental health issues has witnessed a
notable uptick, leading to a substantial disparity between the
demand for mental health services and the available resources
[1]. Consequently, patients frequently encounter prolonged
wait times before they can commence therapy [1], [2]. To
tackle this predicament, a potential remedy emerges in the
form of virtual agents designed to replicate Motivational
Interviews (MI) for patients awaiting available appointments.
These virtual agents hold promise in alleviating the waiting
predicament by offering instantaneous support, particularly
within therapeutic modalities involving multiple sessions [3].
MI is a therapeutic approach underscored by collaboration
and the encouragement of behavioral transformation. During
Motivational Interviews, therapists employ various strategies
to guide patients toward articulating their motivation for
change. These strategies can be composed of verbal (reflection,
question) and nonverbal elements (smiles, head and body
position). A virtual agent using both verbal and nonverbal
ANR Tapas

strategies to conduct motivational interviews could possess
the capacity to rekindle the user’s motivation whenever necessary. Nonetheless, creating such an agent necessitates the
examination of Human-Human data, which proves challenging
to obtain due to the sensitive nature of the subjects discussed. Furthermore, delving into the multimodal conduct of
therapists would provide invaluable insights into the agent’s
development, given that psychological theory underscores the
significance of nonverbal behavior during such interviews [4].
Another aspect highlighted by psychological theory is the
pivotal role of empathic and social conduct. Patients are more
likely to be honest and share their symptoms and concerns
with an empathic physician, leading to better therapy outcomes
[5]. Clinical empathy implies perceiving how the patient is
experiencing the world and how the patient is currently feeling.
In this paper, we present a series of multimodal annotations
and analyses carried out on two existing MI corpora, namely
AnnoMI [6], and the Motivational Interviewing Dataset (MID)
[7]. These annotations aim to scrutinize the empathic conduct
of therapists during MI sessions, along with the behaviors
and responses of patients to such empathic interactions. These
annotations form the Empathic Multimodal Motivational Interviews (EMMI) dataset.
This paper offers the following contributions. First, we
perform multimodal annotations of publicly available MI corpora, creating EMMI. Then, we analyze patients’ behaviors,
highlighting three different types of patients. Finally, we
analyze therapists’ multimodal behavior depending on the type
of patient they interact with.
a) Research Questions: The study of multimodal interaction in therapy can yield a comprehensive understanding of
therapist and patient behavior that can be used to develop a
multimodal virtual agent supporting therapy. Currently, most
datasets in this field primarily focus on the verbal aspect,
only considering limited information from nonverbal behavior.
Existing studies often concentrate on comparing high- and
low-quality interactions, neglecting a deeper analysis of social behaviors. Our research analyzes therapy session videos,
considering the patients’ and therapists’ progression on verbal
and nonverbal levels and their alignment. This investigation
aims to address such questions and gain insights into the
interactions and patterns between the therapist and the patient.

---

Our primary objective is to discern how therapists blend their
task goal (employing classical steps of MI) with their social
goal (building a trusting relationship and expressing empathy).
We also examine how these goals manifest in their verbal
and nonverbal behaviors. Furthermore, this study aims to
uncover how patients respond to different therapeutic strategies
employed by therapists and identify cues indicative of positive
effects on patients, potentially leading to categorizing patients
into various “types” requiring tailored therapeutic approaches.
Lastly, we strive to determine the reciprocal influence of
behaviors between the two interlocutors during the therapeutic
process.
We address the following research questions:
RQ1: Do the behavior of the therapist and the patient evolve
throughout the interaction?
RQ2: Can distinct “types” of patients be identified regarding the change in talk patterns, and to what extent do they
lead to differences in patients’ and therapists’ behavior?
RQ3: How do therapists adapt their verbal and nonverbal
behavior to the talk types of patients?
By investigating these research questions, we aim to gain
insights into multimodal interaction during therapy and contribute to developing effective and personalized virtual therapeutic interventions.
In the next section, MI is defined, existing MI corpora
are presented, and EMMI is presented. Section III describes
our annotation process and introduces different types of MI
patients. In Section IV, we analyze our annotations to highlight differences in the behaviors of patients and therapists
depending on their type, change talk, or whether it is the first
or the second half of the conversation. Finally, in SectionV,
we interpret these differences and discuss the impact of types
on both the patient’s and therapists’ behavior.
II. BACKGROUND AND E XISTING C ORPORA
a) Motivational interviewing: Motivational Interviewing
(MI) is an approach to therapy that emphasizes collaboration
and encourages behavioral change. During MI, therapists
use strategies to guide patients toward expressing motivation
toward change [8]. One of the main strategies is using reflections, where therapists convey their understanding of what
the patient is saying or feeling without judging, interpreting,
or advising. Patient behaviors are classically coded into three
categories defined by the Motivational Interviewing Skill Code
(MISC) [9] with Change talk (CT) reflecting actions toward
behavior change, Sustain talk (ST): reflecting actions away
from behavior change, Follow/Neutral (F/N): unrelated to the
target behavior.
b) Existing corpora: Numerous studies have delved into
exploring MI at the verbal level. However, a significant
challenge arises from the unavailability of relevant data due
to the sensitive nature of the topics discussed within MI
conversations. Most Human-Human MI corpora cannot be
publicly disseminated or are privately owned. For instance,
research by [10], [11] analyzes therapist behavior using phone
conversation transcripts of actual therapy sessions, but these

datasets cannot be shared. [12] collected a private corpus of
audio-recorded therapy session interactions to study therapist
empathy. Similarly, [13] focuses on patient behavior classification using transcribed audio data, with only publicly available
text transcripts.
The preceding corpora are based on audio recording, making
the study of nonverbal behaviors impossible. Although some
video-based corpora have emerged, such as the Counseling and
Therapy Video Library, they are privately owned and often can
be acquired at a high cost. Only a few corpora (not publicly
available) exist to study facial expressions and body language;
for example, [14] assembles a video corpus for detecting
change talk, but it is inaccessible. On the other hand, there
have been recent efforts to create publicly available datasets.
[7] introduces a corpus of MI videos scraped from the web,
though automatic YouTube captioning leads to transcription
errors. Additionally, [6] provides a publicly accessible MI
video corpus transcribed and annotated by experts. ANNOMI
comprises high-quality interactions designed to teach good
practices in MI and low-quality interactions designed to show
mistakes to avoid during an MI intervention. These studies
primarily focus on text analysis, particularly the behavior of
therapists of varying qualities.
However, none of these publicly available resources delve
into the video and audio modalities, nor do they explore how
patients’ behavior varies during a session and how therapist
adapts their strategies during the interaction. This paper addresses this gap by presenting a comprehensive development
and analysis of a multimodal therapist behavior dataset. The
dataset is collected from online open sources, making it
accessible to the broader research community.
c) EMMI: EMMI comprises 285 videos, representing
21 hours and 22 minutes, complementing two pre-existing
datasets: AnnoMI [6] and the MID [7]. These datasets consist
of simulated motivational interview (MI) conversations in
which actors portray the roles of patients and therapists.
However, it is essential to note that these corpora were initially
designed for natural language analysis and do not encompass
the multimodal aspects in the accompanying videos. Thus,
our study aims to fill this gap by considering and analyzing
the multimodal elements within these videos, enabling a
more comprehensive understanding of therapeutic interactions.
These corpora initially focus on the task goal of the conversation; we perform additional annotations to study the social
aspect of motivational interviewing.
d) AnnoMi: AnnoMI is a publicly available dataset of
132 expert-annotated MI videos. Twelve were removed because they were no longer accessible (3) or of poor quality
(9). The selected part of AnnoMi represents 13 hours and 25
minutes of videos. The videos are transcribed and classified
between high- and low-quality MI. Each turn is annotated
based on the primary therapist’s verbal behavior (question,
reflection, other) and the patient’s talk type (neutral, change,
sustain).
e) Motivational Interviewing Dataset (MID): The MID
is similar to AnnoMI, comprising 247 publicly available

---

simulated MI conversations. Eighty-two of these are removed
because some of the videos are already part of the AnnoMI
dataset (39), are missing (37), or are of poor quality (6). The
selected part of the corpus represents 7 hours and 56 minutes.
The videos are transcribed, but the transcriptions are of poor
quality.

(a) Both (b) Only (c) Only (d) Edited (e) Edited
interlocu- patient
therapist patient vis- therapist
tor visible visible
visible
ible
visible

Fig. 1: Example of video settings
f) Videos pre-processing: In preparation for automated
annotations, the videos from the MID are transcribed anew
using the transcription service Descript. To facilitate analysis and comparison of simultaneous nonverbal behavior, the
original videos, which featured different views (i.e., patientonly, therapist-only, or both visible from the side), are edited
to create three standardized views for each video: patientonly view, therapist-only view, and both patient and therapist
visible (see Fig.1). These different views imply that non-verbal
behaviors are not accessible to every interlocutor at every instant, which should be considered for the subsequent analysis.
By segregating the videos into these three distinct views, we
can quickly identify and compare the visible individual’s nonverbal behavior during relevant interaction segments. Furthermore, two additional annotations are generated: An annotation
of who is currently visible in the video (patient, therapist, or
both) and an annotation of the speaker identity (i.e., who has
the speaking turn, the therapist or the patient).
III. M ULTIMODAL ANNOTATIONS
In the following sections, we study different aspects of
the therapist and patient behaviors. We examine task-related
behaviors, encompassing the dialog acts used during the conversation that reflect the classical steps of MI [15]. Additionally, we explore the concept of behavior expressivity, gauged
through indicators like gesture amplitude and loudness, which
offer insights into the confidence levels of the interlocutors
and are also a sign of empathy [16]. This dimension helps
us understand how self-assured the therapist and patient feel
during the interaction. Our investigation also encompasses
social-related behaviors, such as smiles and social dialog acts,
which provide valuable insights into the evolving dynamics
and rapport between the therapist and the patient [5]. Finally,
we look at the alignment between the therapist and the patient
through verbal alignment (How much verbal expressions of
the interlocutor are reused) and amplitude alignment (How
similar the amplitude of the two interlocutors are) [17]. Since
interlocutors’ faces are not always fully visible in the videos,
we choose not to analyze facial expression alignment.
a) Separation in dialog turns: To analyze the interaction,
the corpus is separated into dialog turns. A dialog turn comprises a sequence of dialog acts that correspond to utterances.

During a dialog turn, the listener can produce a backchannel
that does not interrupt the turn. For each dialog turn, we give
the number of backchannels performed by the listener and
their timing and form.
b) Dialog act: Dialog acts are annotated using a schema
derived from [18]. Using multilabel annotation, patients’ dialog turns are classified into one or multiple of the dialog acts
defined in Table I. Therapists’ dialog turns are classified into
one or multiple of the task-oriented dialog acts and/or one
of the socially oriented dialog acts described in Table II. The
dialog turns are classified using Mistral instruct [19] and few
shots learning. Mistral instruct is an open-source, free model
usable with an NVIDIA RTX A2000 GPU 8GB. The prompt
is derived from [18]. The automatic annotations are tested
on a subpart of the HOPE dataset [20]. The HOPE dataset
comprises CBT and MI videos with good-quality transcripts
overlapping with AnnoMI. The resulting automatic classifier
will, therefore, be transferable to EMMI. We used HOPE to
test the classifier and validate it on both MI and CBT.500
dialog turns of the patient and 500 of the therapist have been
annotated twice with one week delay by one of the paper’s
authors with a Cohen kappa alpha agreement of 0.65 for the
patient and 0.7 for the therapist. These annotated sentences
are used to validate the automatic annotations with a macroF1 score of 0.69 for the patient and the therapist (see F1 values
for each dialog act in I for the patient and II for the therapist).
The prompts and the annotations are available on github1 .
c) Verbal alignment: is computed using Dialign [22]. It
computes the number of reused verbal expressions initiated by
the other interlocutor.
d) Loudness: , the intensity of the voice is annotated
using OpenSmile [23].
e) Face Features: for the therapist and the patient are
collected using OpenFace [24]. The action units are filtered
with a median filter of size 3 and interpolated for missing
values.
f) Smile: are detected using the HMAD project [25] that
annotates smiles on the five levels of the Smiling Intensity
Scale based on features extracted with OpenFace.
g) The body joints’ position and orientation: are collected using OpenPose. [26]
h) Amplitude: The amplitude of the upper body is defined as the bounding box around the speaker for a given time
frame. It is computed by dividing the distance between the
two wrists by the height of the bust in the current frame.
i) Change talk: The Motivational Interviewing Skill
Code (MISC) categorizes patient talk into three distinct classifications: Change Talk that denotes the expression of behaviors aligned with embracing change, Sustain Talk that refers
to the articulation of behaviors demonstrating a rejection of
change, Neutral Talk that encompasses behaviors unrelated
to the targeted change. The MISC classification scheme carries
significance due to its demonstrated correlation with therapy
outcomes [27], [28]. Moreover, the talk type has already been
1 https://github.com/l-Galland/MI-DA-classification

---

Definition
Changing
unhealthy behavior
Sustaining
unhealthy behavior
Sharing negative
feeling or emotion
Sharing positive
feeling or emotion
Realization or
Understanding
Shapersonalonnal
information
Greeting or Closing
Backchannel
Asking for medical
information
Macro average

macro-F1

Recall

Accuracy

The patient explicitly expresses their willingness to change

0,80[0,76;0,84]

0,78[0,74;0,83]

0,89[0,87;0,91]

The patient explicitly expresses their unwillingness to change

0,61[0,55;0,67]

0,60[0,55;0,66]

0,89[0,87;0,91]

The patient shares a negative feeling or vision of the world

0,63[0,59;0,68]

0,62[0,58;0,65]

0,80[0,78;0,83]

The patient shares a positive feeling or vision of the world

0,65[0,54;0,77]

0,80[0,59;0,99]

0,98[0,96;0,99]

The patient realized or understood something about their problem

0,63[0,55;0,71]

0,63[0,55;0,72]

0,94[0,93;0,96]

The patient shares factual personal information about their situation
or background
The patient opens or closes the conversation
The patient acknowledge that they heard the last therapist’s statement

0,69[0,65;0,72]

0,71[0,67;0,75]

0,70[0,66;0,73]

0,76[0,65;0,85]
0,65[0,59;0,72]

0,75[0,63;0,87]
0,80[0,71;0,89]

0,98[0,96;0,99]
0,90[0,89;0,92]

The patient ask for medical information

0,74[0,57;0,87]

0,86[0,59;0,99]

0,99[0,98;0,99]

0,69[0,65;0,72]

0,73[0,69;0,77]

0,90[0,89;0,90]

TABLE I: Classification scores of patients dialog act. The 95% confidence intervals are computed using the bootstrap method
and a 1000 runs [21]
Definition
Ask for consent
or validation
Medical
Education
and Guidance
Planning with
the patient
Give Solution
Ask about
current
emotions
Invite to shift
outlook
Ask for
Information
Reflection
Empathic
reaction
Acknowledge
progress and
encourage
Backchannel
Greeting or
Closing
Experience
Normalization
and Reassurance
Macro average

Macro F1 score

Recall

Accuracy

0,67[0,55;0,78]

0,77[0,61;0,98]

0,97[0,96;0,98]

0,83[0,74;0,89]

0.83[0,73;0,91]

0,97[0,96;0,98]

0,73[0,67;0,79]

0,70[0,65;0,76]

0,92[0,90;0,94]

0,66[0,59;0,73]

0.67[0,59;0,76]

0,94[0,92;0,95]

0,64[0,60;0,69]

0,62[0,57;0,66]

0,88[0,85;0,90]

0.57[0.51;0.63]

0.56[0,52;0,61]

0,91[0,88;0,93]

0.78[0.75;0.81]

0,81[0,78;0,84]

0,80[0,77;0,83]

0.73[0.69;0.76]

0.72[0,68;0,76]

0,77[0,74;0,80]

The therapist expresses empathy to the patient

0,62[0,53;0,71]

0.68[0,55;0,82]

0,96[0,94;0,97]

The therapist praises the patient for their achievements or encourages them

0,62[0,53;0,71]

0.87[0,67;0,98]

0,96[0,94;0,97]

The therapist acknowledges that they heard the last patient’s statement

0,65[0,56;0,74]

0,83[0,68;0,98]

0,96[0,95;0,97]

The therapist open or closes the conversation

0,85[0,77;0,93]

0.88[0,79;0,96]

0,98[0,96;0,95]

The therapist normalizes the patient experience and reassure them

0,59[0,49;0,68]

0.58[0,49;0,68]

0,97[0,95;0,98]

0,69[0,67;0,71]

0.73[0,70;0,76]

0.92[0,91;0,93]

Task oriented Dialog acts
The therapist checks that their last statement was correct or
that the patient consented to move forward
The therapist provides the patient with medical or therapeutic facts
The therapist builds a plan with the patient to modify
their unhealthy behavior/thoughts
The therapist provides the patient with solutions to solve their problem
The therapist ask the patient what they are feeling during the therapy session
The therapist asks the patient to imagine their reaction to a future event or
to change their perspectives on a past even
The therapist asks the patient factual information
about their background or situation
The therapist summarize or reformulate the patient statement without judgment
Socially oriented Dialog acts

TABLE II: Classification scores of therapists dialog act. The 95% confidence intervals are computed using the bootstrap method
and a 1000 runs [21]

annotated within AnnoMI. Previous work trained a multimodal
classifier using this annotated data, yielding an F1 score of 0.8
[29]. This classifier is employed to annotate the MID in terms
of change talk.2
j) Patient clustering: Each patient utterance in EMMI
is annotated at the level of change talk: [neutral, sustain,
change]. This annotation is transformed into a numerical
2 This classification into change/ sustain/ neutral is different from the one
carried out in SectionIII-0b as it considers all modalities and not only the
text. This classification also takes into account subtext that is not taken into
account by the dialog act classifier and is therefore complementary

score of change talk where sustain = -1, neutral = 0, and
change = 1. We apply the KMeans algorithm with a DTW
metric [30] to compute clusters of patients. The DTW metric
accounts for similar patterns in change talk behavior even
when the timing or length of the pattern is not precisely
identical. The Elbow method [31] shows that the optimal
number of clusters is 3 with a silhouette score of 0.17. The
visualization of the clusters of patients as well as a timebased analysis (see Fig. 2) shows three types that can be
concretely interpreted; Patient type (Kruskal-Wallis H test:

---

Hchange (2) = 18.1,pchange = 1.2e − 4, Hsustain (2) = 20.5,
psustain = 3.5e − 5) and Time (Kruskal-Wallis H test:
Hchange (1) = 40.7,pchange = 1.8e − 10, Hsustain (1) =
12.17, psustain = 5.1e − 4) have a significant main effect on
both change and sustain talk proportion for at least two groups.
The following Mann-Whitney U post hoc test results can be
seen in Table III and Figure 2. Since [32] states that “Patient
stuck in ambivalence engages in a lot of sustain talk, whereas
patients who are more ready to change engage in more change
talk with stronger statements supporting change,” we can then
interpret our clusters as the following:
• When the patient begins the conversation with significantly less sustain talk than other patients (p < 1e − 4)
and significantly more change talk than other patients
(p < 5e − 2), we define them as ”Ready to change”
• When the patient displays significantly less change talk
throughout the conversation than other patients (p < 5e−
3), we define them as ”Resistant to change”
• When the patient starts with a comparable number of
sustain talk as “Resistant to change” patients but more
change talk (p < 5e − 2) and the patient displays
significantly more change talk than “Resistant to change”
patient, especially during the second half of the conversation (p < 1e − 2), we define them as ”Receptive”
Beg

End

p change
4.0e-12 (****)

p sustain
3.9e-5 (****)

Rec
Rec
Op

Op
Res
Res

9.5e-1
3.8e-3 (**)
2.0e-2 (*)

5.2e-7 (****)
2.6e-5 (****)
5.5e-1

Beg

Rec
Rec
Op

Op
Res
Res

9.7e-2 (.)
1.2e-5 (****)
2.6e-2 (*)

1.2e-7 (****)
1.2e-2 (*)
1.9e-1

End

Rec
Rec
Op

Op
Res
Res

2.6e-1
1.1e-1
4.3e-2 (*)

1.6e-1
1.3e-2
6.1e-1

TABLE III: Post hoc test on patient talk type depending on
patients type and time . p<0.1, * p<0.05, ** p<0.01, ** p<0.001,
*** p<0.0001, **** p<0.00001
Beg = First half, End=Second half, Op = Ready to change,
Rec=Receptive, Res = Resistant to change

(a) Sustain talk

IV. M ULTIMODAL BEHAVIOR ANALYSIS
In this section, we investigate our three research questions
through the length of the targeted behaviors described in
Section III: task behavior, expressivity, social behavior, and
alignment. Section V discusses the reported statistical results.
We study the differences in target behaviors between the first
and second half of the conversation to study the evolution
during the interaction (RQ1). We separated the interaction
into two parts, as the small number of videos does not allow
for more fine-grained studies. We also study the differences
between different types of patient talk (RQ2) and talk types
(RQ3). We use non-parametric tests whenever the normality
requirements for ANOVA are not met. All p-values are corrected using the Bonferroni method. For clarity purposes, we
do not report every test value in the following section. We
also focus on the high-quality part of the corpus as we aim to
develop a high-quality virtual therapist.
A. Task related behavior
a) Therapist dialog acts: Therapist plan more with the
patient during the second half than during the first half of the
conversation (T-test: p = 0.02). There is also a difference in
the use of planning according to at least two groups of patient
types (Kruskal-Wallis H test: p = 0.03). Therapists plan
significantly more with “Receptive” than with “Resistant to
change” (Mann-Whitney U test: p = 0.04). The therapist asks
for more information during the first half of the conversation
(T-test: p = 0.003), but there are no significant differences
between patients’ talk types (Kruskal-Wallis H test: p = 0.84).
There are no significant differences between the first and
the second half of the conversation in the use of invitation
to shift outlook (T-test: p = 0.12). However, there is a
difference between at least two groups of patients for the
invitation to shift outlook (Kruskal-Wallis H test: p = 0.02).
The therapist invites significantly more to shift outlook when
interacting with a “Receptive” patient than when interacting
with a “Resistant to change” patient (Mann-Whitney U test:
p = 0.05).
b) Patient dialog act: The patient expresses significantly
more intention to change unhealthy behaviors during the
second half of the conversation than during the second half
(T-test: p = 0.0005). There is also a difference in the use
of changing statements according to at least two groups of
patient types (Kruskal-Wallis H test: p = 0.03). Patients use
significantly fewer change statements when they are “Resistant
to change” than when they are “Receptive” (Mann-Whitney U
test: p = 0.03). Patients share more information during the
first half of the conversation than during the second half (Ttest: p = 0.002). Yet, there are no differences between patient
types (Kruskal-Wallis H test p = 0.73).

(b) Change talk

B. Expressivity related behaviors
Fig. 2: Evolution of change and sustain talk in time according
to patient type . p<0.1, * p<0.05, ** p<0.01, ** p<0.001,***
p<0.0001, **** p<0.00001

a) Amplitude: Patients show significantly more amplitude during the first half than during the second half of
the conversation (T-test: p = 0.04), while no significant
differences are observed for the amplitude of the therapist

---

between the first and the second half of the conversation (Ttest: p = 0.45); significant differences are observable between
patient types for the patient’s body amplitude (Kruskal-Wallis
H test: p = 7.4e − 11). “Resistant to change” patients
display more amplitude, while “Receptive” patients display
smaller motions with less amplitude (Mann-Whitney U test:
all p < 1e − 4). There are no significant variations in
amplitude between groups for patients (Kruskal-Wallis H test:
H(2) = 0.06, p = 0.97) and therapists (Kruskal-Wallis H test:
H(2) = 3.7, p = 0.16).
b) Loudness: There are variations in patient loudness
between the start of the conversation and its ending (Ttest: p = 0.003). Specifically, patients exhibit a higher
voice volume towards the dialogue’s end, although such a
trend isn’t mirrored in therapist loudness (T-test: p = 0.29).
There are notable differences in loudness across various patient types for both patients and therapists (Kruskal-Wallis
H test: Hpatient (2) = 53.18, ppatient = 2.84e − 12 and
Htherapist (2) = 58.9, ptherapist = 1.61e − 13). Both patients
and therapists speak more loudly when they resist change and
adopt a softer tone when the patient is “Ready to change”
(Mann-Whitney U test: all p < 5e − 2). This difference is not
significant between the therapists interacting with “Receptive”
and “Resistant to change” patients (Mann-Whitney U test:p =
0.3) (see Fig.3). Furthermore, loudness discrepancies related
to expressed talk types emerge among patients (Kruskal-Wallis
H test: H(2) = 23.47, p = 8e − 6). Patients speak at a higher
volume when expressing “sustain talk” than “change talk” and
“neutral talk” (Mann-Whitney U test: all p < 0.006).

(a) Patient loudness

(b) Therapist loudness

Fig. 3: Evolution of loudness separated by types . p<0.1, *
p<0.05, ** p<0.01, ** p<0.001,*** p<0.0001, **** p<0.00001

C. Social related behaviors
a) Therapist social dialog acts: There are no significant
differences between the first and the second half of the
conversation in the use of empathic reaction (T-test: p = 0.41).
However, there is a difference between at least two groups
of patients (Kruskal-Wallis H test: p = 0.04). The therapist
tends to use more empathic reactions when interacting with a
“Receptive” patient than when interacting with a “Resistant to
change” patient (Mann-Whitney U test: p = 0.08).
b) Smiles: There are no significant differences in the
number of therapists’ smiles between the first and second half
of the conversation (T-test: p = 0.4). However, their smiles last

longer in the second half (T-test: p < 1e − 6). On the other
hand, the patient smiles less during the second half of the
interaction (T-test: p < 1e − 46) but with more prolonged (Ttest: p < 1e−15) and more intense smiles (T-test: p < 1e−22).
There is a difference between at least two groups of patients
in smiles of patients and therapists for the number of smiles
(Kruskal-Wallis H test: ppatient < 1e − 30, ptherapist <
1e − 30), duration (Kruskal-Wallis H test: ppatient < 1e − 19,
ptherapist < 1e − 12) and intensity (Kruskal-Wallis H test:
ppatient < 1e − 10, ptherapist < 1e − 6). Patients smile more
when they are “Resistant to change” and less when they are
“Ready to change” (Mann-Whitney U test: all p < 1e − 30).
However, patients’ smiles are longer when they are “Ready to
change” and less long when they are “Resistant to change”
(Mann-Whitney U test: all p < 1e − 2). Smiles are also
significantly more intense when patients are “Resistant to
change” and less intense when they are “Ready to change”
(Mann-Whitney U test: all p < 1e − 5). Therapists smile more
when patients they are interviewing are “Resistant to change”
and less when they are “Ready to change” (Mann-Whitney U
test: all p < 1e − 30). Smiles last longer when the patient
is “Ready to change” and shorter when they are “Receptive”
(Mann-Whitney U test: all p < 5e − 2). Smiles are more
intense when the patient is “Resistant to change” and less
intense when the patient is “Ready to change” (Mann-Whitney
U test: all p < 1e − 30). There is a difference between at least
two different types of patient talk for the therapists’ and the
patients’ smiles in terms of number (Kruskal-Wallis H test:
ppatient < 7e − 3, ptherapist < 1e − 27), duration (KruskalWallis H test: ppatient < 1e − 30, ptherapist < 1e − 30)
and intensity (Kruskal-Wallis H test: ppatient < 4e − 6,
ptherapist < 1e − 11). Patients smile more when they express
neutral talk than when they listen (Mann-Whitney U test:
p < 5e − 2). When the patient is listening, their smiles last
significantly longer (Mann-Whitney U test: p < 1e − 30),
and their smiles are significantly more intense than when
they have the speaking turn and express neutral or sustain
talk (Mann-Whitney U test: p < 3e − 2). Therapists smile
significantly more when they have the turn (Mann-Whitney
U test: p < 1e − 7); they also smile more when they listen
to neutral talk than when they listen to change talk (MannWhitney U test: p = 3e − 2). They also smile significantly
longer(Mann-Whitney U test: p < 1e − 30) and intensely
(Mann-Whitney U test: p < 9e − 5) when they have the turn.
D. Alignment
a) Verbal alignment: The Dialign tools [22] provide for
each utterance the list of verbal expressions initiated by an
interlocutor that the other interlocutor reuses. Throughout the
dialogue, there is a discernible upward trend in the recurrence
of verbal expressions, both for therapist-initiated and patientinitiated utterances. There is a notable variance in repeated
expression based on the type of patient talk and the type
of patient (Kruskal-Wallis H test: all p < 0.02). A higher
frequency of expressions is reused when patients convey
neutral statements (Mann-Whitney U test: all p < 1e − 11).

---

Additionally, the therapist reuses more of the patient’s expressions when the patient is categorized as “Ready to change” or
“Receptive” (Mann-Whitney U test: all p < 3e − 4).
b) Amplitude alignment: The alignment of the amplitude
between the patients and the therapists is quantified by the
absolute value of the difference between the therapist’s and
the patient’s amplitude. There are statistical differences in
alignment between at least two types of patients (KruskalWallis H test: H(2) = 12, p = 0.002). “Receptive” patients are
significantly more aligned with their therapists than “Resistant
to change” patients (Mann-Whitney U test: p = 1e − 6) and
“Ready to change” patients (Mann-Whitney U test: p = 0.02).
There are no differences between patient talk types (KruskalWallis H test: H(2) = 0.19, p < 0.9).
V. D ISCUSSION
a) Task related: Throughout the conversation, we observe an evolution of the dialog acts used by the therapist and
the patient (RQ1). During the first half of the conversation,
the therapist asks many questions to assess the context and
concerns of the patient. In contrast, the patient shares personal
information to answer those questions. During the second half
of the conversation, the therapist makes more statements about
planning and advises the patients on addressing their problems.
In response, the patient has more intention to change, reacting
to the therapist’s input. However, this global evolution can vary
depending on the type of patient (RQ2). The therapist uses
more invitation to shift outlook when the patient is classified
as “Receptive” than when they are classified as “Resistant to
change.” This may imply that therapists attempt to provide new
perspectives to patients who appear open to receiving them but
have not yet determined their motivation to change (namely,
the “Receptive” ones). Furthermore, patients classified as
“Resistant to change” tend to manifest behaviors indicative of
a reluctance to engage in dialogue and use significantly fewer
statements explicitly directed toward changing their behaviors.
b) Behavior expressivity: We observe an evolution in the
behavior expressivity of the patients throughout the conversation (RQ1). Indeed, patients tend to be physically more
expressive in the second half of the conversation, where they
talk more loudly and display behavior with larger amplitude.
These observable changes suggest a growing confidence and
self-assurance as the dialogue unfolds. Differences in this
degree of expressivity are also observable between patient
types (RQ2). In particular, “Resistant to change” patients
exhibit a more pronounced behavior expressivity, characterized
by louder speech and a more openly engaged demeanor than
other patient types. This observation implies that these patients
are significantly more assertive and self-assured about their
viewpoints [33]. Similarly, patients are louder when they
perform sustain talk (RQ3). An interpretation of these results
is that patients who are “Resistant to change” or expressing
sustained talk when faced with an MI therapist are confident in
their beliefs [34], which might explain why it is more difficult
to change their minds.

c) Social behaviors: The interpersonal relations between
the patient and the therapist improve significantly as the
interaction progresses (RQ1). The duration and intensity of
smiles from the patient and the therapist increase in the
second half of the interaction. Social behaviors are particularly
pronounced when the patient engages in what can be termed
“neutral talk” (RQ3), characterized by a more positive outlook
and longer-lasting smiles. Interestingly, the patient also tends
to convey a more positive demeanor when expressing “change
talk” instead of “sustain talk”. Furthermore, when both the
therapist and the patient express shared goals, there is a distinct
increase in social behaviors between the two interlocutors.
While it is noted that social behaviors are generally more
present with patients who are “Ready to change” compared
to those who exhibit resistance (RQ2), this relationship is
nuanced. Therapists tend to use more emphatic statements with
Receptive patients than patients who are “Resistant to change”.
“Ready to change” patients display a more positive disposition,
with longer-lasting smiles, suggesting a natural alignment with
the therapeutic process. Patients who are “Resistant to change”
tend to smile more and more intensely. These smile patterns
are mirrored by the therapist, indicating an effort from the
therapist to foster interpersonal relations with “Resistant to
change” patients, likely to enhance the therapeutic outcome.
d) Alignment: The alignment between the therapist and
the patient tends to grow throughout the conversation (RQ1).
More expressions are reused in the second half than in the first
half. This alignment is also more potent when the patient is
“Ready to change” and “Receptive” (RQ2). The amplitude
of the patient’s and therapist’s bust is more aligned when
the patient is “Ready to change” and “Receptive”, and more
expressions are reused. Such alignment emerges as the goals
of the therapist and the patient are also more aligned. A high
verbal alignment can also be a sign of engagement [35]. These
results can, therefore, be a sign that “Ready to change” and
“Receptive” patients are more engaged in the conversation
with the therapist as their initial goal (changing their behavior)
is validated by the conversation.
VI. C ONCLUSION
This paper presents EMMI, composed of two publicly
available corpora, AnnoMI and MID, for which we have
added multimodal annotations. We analyze these annotations
to extract pertinent behavior for developing a virtual agent
performing motivational interviews emphasizing social behaviors. We highlight differences in behavior for both the therapist
and the patient during the conversations and depending on
the change talk conducted by the patient. Our analysis shows
that patients can be clustered into three groups of patients
(“Ready to change”, “Resistant to change”, and “Receptive”)
whose behavior differs significantly. The therapist also exhibits
different behaviors depending on the type of interlocutor. This
shows the importance of virtual interviewers to adapt their behaviors depending on the type of their human patient and their
current behavior. In future work, identifying and characterizing
these patient types could be a foundation for developing a

---

multimodal dialog to deliver customized MI interventions.
The insights gained from understanding how patients evolve
in their communication style, behavior expressivity, social
and empathic behaviors, and alignment throughout the conversation can inform the design of an intelligent virtual MI
interviewer that could dynamically adapt its communication
strategies, voice, and content based on the identified type of
patient, thus enhancing the effectiveness of MI.
ACKNOWLEDGMENT
This work was partially funded by the ANR-DFG-JST
Panorama and ANR-JST-CREST TAPAS (19-JSTS-0001-01)
projects.
E THICAL I MPACT S TATEMENT
While the primary aim of our research is not to replace
therapists but rather to extend support and accessibility to
underserved populations, the personalized adaptability we
propose could inadvertently open avenues for manipulation.
Introducing an empathetic virtual therapist also raises concerns
regarding human-agent attachment, which necessitates careful
consideration. In our final application, we are committed to
transparently informing participants that they are engaging
with a virtual therapist, one that is fallible, may make mistakes,
and lacks emotional capacity. It is crucial to emphasize that
the agent is not a substitute for human-to-human therapy.
The annotations conducted on videos sourced from YouTube
feature actors and do not include any personally identifiable
information, thus safeguarding privacy. While the use of actors
may introduce a bias, it also allows for privacy protection.
Acknowledging that our data primarily consists of interactions with American participants introduces a potential bias
in dialog acts classification results, particularly concerning
vocabulary usage. To mitigate this risk, we aim to incorporate
examples from other dialects, such as British or AfricanAmerican Vernacular English, to enhance the classifier’s adaptability across diverse linguistic contexts. The proposed dialog
act classifier will be used as a natural language understanding
module within human-agent conversations. However, it is
imperative to recognize that automatic classifications can yield
errors, particularly in the sensitive context of therapy, where
mistakes can have significant repercussions. Consequently,
outputs from the classifier should be handled with utmost care.
This is also true of the proposed separation of patients into
types. In contrast to prevailing methodologies, we have opted
to utilize the open-source Mistral model instead of OpenAI’s
GPT. This enables cost-free usage, open-source availability,
and offline deployment. Given the importance of maintaining
patient privacy in the context of utterance classification in
therapy, the ability to operate the model offline is essential.
R EFERENCES
[1] G. Cameron, D. Cameron, G. Megaw, R. Bond, M. Mulvenna,
S. O’Neill, C. Armour, and M. McTear, “Towards a chatbot for digital
counselling,” in Proceedings of the 31st International BCS Human
Computer Interaction Conference (HCI 2017) 31, 2017, pp. 1–7.

[2] K. Denecke, S. Vaaheesan, and A. Arulnathan, “A mental health chatbot
for regulating emotions (sermo)-concept and usability test,” IEEE Transactions on Emerging Topics in Computing, vol. 9, no. 3, pp. 1170–1182,
2020.
[3] A. Fiske, P. Henningsen, and A. Buyx, “Your robot therapist will see
you now: ethical implications of embodied artificial intelligence in
psychiatry, psychology, and psychotherapy,” Journal of medical Internet
research, vol. 21, no. 5, p. e13216, 2019.
[4] D. G. Gillam and H. Yusuf, “Brief motivational interviewing in dental
practice,” Dentistry Journal, vol. 7, no. 2, p. 51, 2019.
[5] B. D. Jani, D. N. Blane, and S. W. Mercer, “The role of empathy
in therapy and the physician-patient relationship,” Forschende Komplementärmedizin/Research in Complementary Medicine, vol. 19, no. 5, pp.
252–257, 2012.
[6] Z. Wu, S. Balloccu, V. Kumar, R. Helaoui, D. Reforgiato Recupero, and
D. Riboni, “Creation, analysis and evaluation of annomi, a dataset of
expert-annotated counselling dialogues,” Future Internet, vol. 15, no. 3,
p. 110, 2023.
[7] V. Pérez-Rosas, X. Wu, K. Resnicow, and R. Mihalcea, “What makes a
good counselor? learning to distinguish between high-quality and lowquality counseling conversations,” in Proceedings of the 57th Annual
Meeting of the Association for Computational Linguistics, 2019, pp.
926–935.
[8] W. R. Miller and S. Rollnick, Motivational interviewing: Helping people
change. Guilford press, 2012.
[9] W. R. Miller, T. B. Moyers, D. Ernst, and P. Amrhein, “Manual for the
motivational interviewing skill code (misc),” Unpublished manuscript.
Albuquerque: Center on Alcoholism, Substance Abuse and Addictions,
University of New Mexico, 2003.
[10] V. Pérez-Rosas, R. Mihalcea, K. Resnicow, S. Singh, and L. An,
“Building a motivational interviewing dataset,” in Proceedings of the
Third Workshop on Computational Linguistics and Clinical Psychology,
2016, pp. 42–51.
[11] V. Pérez-Rosas, R. Mihalcea, K. Resnicow, S. Singh, L. An, K. J.
Goggin, and D. Catley, “Predicting counselor behaviors in motivational
interviewing encounters,” in Proceedings of the 15th Conference of the
European Chapter of the Association for Computational Linguistics:
Volume 1, Long Papers, 2017, pp. 1128–1137.
[12] V. Pérez-Rosas, R. Mihalcea, K. Resnicow, S. Singh, and L. An, “Understanding and predicting empathic behavior in counseling therapy,”
in Proceedings of the 55th Annual Meeting of the Association for
Computational Linguistics (Volume 1: Long Papers), 2017, pp. 1426–
1435.
[13] L. Tavabi, K. Stefanov, L. Zhang, B. Borsari, J. D. Woolley, S. Scherer,
and M. Soleymani, “Multimodal automatic coding of client behavior
in motivational interviewing,” in Proceedings of the 2020 International
Conference on Multimodal Interaction, 2020, pp. 406–413.
[14] Y. I. Nakano, E. Hirose, T. Sakato, S. Okada, and J.-C. Martin,
“Detecting change talk in motivational interviewing using verbal and
facial information,” in Proceedings of the 2022 International Conference
on Multimodal Interaction, 2022, pp. 5–14.
[15] C. Beauvais, “Motivational interviewing to improve treatment adherence,” pp. 535–537, 2019.
[16] S. E. Decker, C. Nich, K. M. Carroll, and S. Martino, “Development of
the therapist empathy scale,” Behavioural and cognitive psychotherapy,
vol. 42, no. 3, pp. 339–354, 2014.
[17] S. P. Lord, E. Sheng, Z. E. Imel, J. Baer, and D. C. Atkins, “More
than reflections: Empathy in motivational interviewing includes language
style synchrony between therapist and client,” Behavior therapy, vol. 46,
no. 3, pp. 296–303, 2015.
[18] Y. Y. Chiu, A. Sharma, I. W. Lin, and T. Althoff, “A computational
framework for behavioral assessment of llm therapists,” arXiv preprint
arXiv:2401.00820, 2024.
[19] A. Q. Jiang, A. Sablayrolles, A. Mensch, C. Bamford, D. S. Chaplot,
D. d. l. Casas, F. Bressand, G. Lengyel, G. Lample, L. Saulnier et al.,
“Mistral 7b,” arXiv preprint arXiv:2310.06825, 2023.
[20] G. Malhotra, A. Waheed, A. Srivastava, M. S. Akhtar, and
T. Chakraborty, “Speaker and time-aware joint contextual learning for
dialogue-act classification in counselling conversations,” in Proceedings
of the fifteenth ACM international conference on web search and data
mining, 2022, pp. 735–745.
[21] B. Efron and R. J. Tibshirani, “An introduction to the bootstrap: Crc
press,” Ekman, P., & Friesen, WV (1978). Manual for the facial action
coding system, 1994.

---

[22] G. Dubuisson Duplessis, C. Langlet, C. Clavel, and F. Landragin,
“Towards alignment strategies in human-agent interactions based on
measures of lexical repetitions,” Language Resources and Evaluation,
vol. 55, pp. 353–388, 2021.
[23] F. Eyben, M. Wöllmer, and B. Schuller, “Opensmile: the munich
versatile and fast open-source audio feature extractor,” in Proceedings
of the 18th ACM international conference on Multimedia, 2010, pp.
1459–1462.
[24] T. Baltrusaitis, A. Zadeh, Y. C. Lim, and L.-P. Morency, “Openface
2.0: Facial behavior analysis toolkit,” in 2018 13th IEEE international
conference on automatic face & gesture recognition (FG 2018). IEEE,
2018, pp. 59–66.
[25] S. Rauzy and A. Goujon, “Automatic annotation of facial actions from a
video record: The case of eyebrows raising and frowning,” in Workshop
on” Affects, Compagnons Artificiels et Interactions”, WACAI 2018,
2018, pp. 7–pages.
[26] Z. Cao, T. Simon, S.-E. Wei, and Y. Sheikh, “Realtime multi-person 2d
pose estimation using part affinity fields,” in Proceedings of the IEEE
conference on computer vision and pattern recognition, 2017, pp. 7291–
7299.
[27] M. Magill, J. Gaume, T. R. Apodaca, J. Walthers, N. R. Mastroleo,
B. Borsari, and R. Longabaugh, “The technical hypothesis of motivational interviewing: A meta-analysis of mi’s key causal model.” Journal
of consulting and clinical psychology, vol. 82, no. 6, p. 973, 2014.
[28] M. Magill, T. R. Apodaca, B. Borsari, J. Gaume, A. Hoadley, R. E.
Gordon, J. S. Tonigan, and T. Moyers, “A meta-analysis of motivational
interviewing process: Technical, relational, and conditional process models of change.” Journal of consulting and clinical psychology, vol. 86,
no. 2, p. 140, 2018.
[29] L. Galland, C. Pelachaud, and F. Pecune, “Seeing and hearing what has
not been said; a multimodal client behavior classifier in motivational
interviewing with interpretable fusion,” 2023.
[30] H. Sakoe and S. Chiba, “Dynamic programming algorithm optimization
for spoken word recognition,” IEEE transactions on acoustics, speech,
and signal processing, vol. 26, no. 1, pp. 43–49, 1978.
[31] R. L. Thorndike, “Who belongs in the family?” Psychometrika, vol. 18,
no. 4, pp. 267–276, 1953.
[32] C. for Substance Abuse Treatment et al., “Enhancing motivation for
change in substance use disorder treatment,” Treatment improvement
protocol (TIP) series, 2019.
[33] E. Vickers, “The loudness war: Background, speculation, and recommendations,” in Audio Engineering Society Convention 129. Audio
Engineering Society, 2010.
[34] K. R. Scherer, H. London, and J. J. Wolf, “The voice of confidence:
Paralinguistic cues and audience evaluation,” Journal of Research in
Personality, vol. 7, no. 1, pp. 31–44, 1973.
[35] H. S. Becker, “Sur le concept d’engagement,” SociologieS, 2006.

---
