# Human review: Groq + dense, 30 validation responses

Status: **awaiting human judgments; 0/30 reviewed**.

Reviewer: Arya. Codex prepares and records; only explicit human judgments count.
All 30 saved dense responses are included in their original order. No new model calls.
Earlier agent labels are omitted. This is a single-reviewer, descriptive validation audit.

For each claim choose fully_supported, partially_supported, unsupported, or unsure.
Judge the answer separately: correct, partially_correct, incorrect, or unsure.
For refusals judge whether the supplied passages justified refusal: yes, no, or unsure.
Errors remain errors and have no claim-support label. Unsure labels stay unresolved.
Benchmark references can be consulted separately after the initial source-support judgment.
Use docs/evaluation.md for the existing rubric. JSON is the record of judgments.

## 1. What data was presented to the subjects to elicit event-related responses?

Paper: `1904.04358`; question: `e6583c60b13b87fc37af75ffc975e7e316d4f4e0`; request: `dd730e979e294c0a8c520d34d5b499d1`.
Saved status: **answered**. Human review: **pending**.

### Claim 1

The subjects were presented with phonemic/syllabic prompts (/iy/, /piy/, /tiy/, /diy/, /uw/, /m/, /n/) and four word prompts (pat, pot, knew, gnaw) to elicit event‑related responses.

Citations: `1904.04358:s0007:p0000:c0000`

Human support: pending. Human note:

### Cited passages

`1904.04358:s0007:p0000:c0000` - Dataset; source characters 0:788.

> We evaluate our model on a publicly available dataset, KARA ONE BIBREF17 , composed of multimodal data for stimulus-based, imagined and articulated speech state corresponding to 7 phonemic/syllabic ( /iy/, /piy/, /tiy/, /diy/, /uw/, /m/, /n/ ) as well as 4 words(pat, pot, knew and gnaw). The dataset consists of 14 participants, with each prompt presented 11 times to each individual. Since our intention is to classify the phonological categories from human thoughts, we discard the facial and audio information and only consider the EEG data corresponding to imagined speech. It is noteworthy that given the mixed nature of EEG signals, it is reportedly challenging to attain a pairwise EEG-phoneme mapping BIBREF18 . In order to explore the problem space, we thus specifically target

Human correctness/refusal judgment: pending.

## 2. Can named entities in SnapCaptions be discontigious?

Paper: `1802.07862`; question: `a0543b4afda15ea47c1e623c7f00d4aaca045be0`; request: `ddad5c2b2d994858a2cd71a143235dcd`.
Saved status: **insufficient_evidence**. Human review: **pending**.

### Supplied passages

`1802.07862:s0006:p0000:c0001` - SnapCaptions Dataset; source characters 756:1344.

> available). We split the dataset into train (70%), validation (15%), and test sets (15%). The captions data have average length of 30.7 characters (5.81 words) with vocabulary size 15,733, where 6,612 are considered unknown tokens from Stanford GloVE embeddings BIBREF22 . Named entities annotated in the SnapCaptions dataset include many of new and emerging entities, and they are found in various surface forms (various nicknames, typos, etc.) To the best of our knowledge, SnapCaptions is the only dataset that contains natural image-caption pairs with expert-annotated named entities.

`1802.07862:s0008:p0000:c0000` - Results: SnapCaptions Dataset; source characters 0:192.

> Table TABREF6 shows the NER performance on the Snap Captions dataset. We report both entity types recognition (PER, LOC, ORG, MISC) and named entity segmentation (named entity or not) results.

`1802.07862:s0006:p0000:c0000` - SnapCaptions Dataset; source characters 0:859.

> The SnapCaptions dataset is composed of 10K user-generated image (snap) and textual caption pairs where named entities in captions are manually labeled by expert human annotators (entity types: PER, LOC, ORG, MISC). These captions are collected exclusively from snaps submitted to public and crowd-sourced stories (aka Snapchat Live Stories or Our Stories). Examples of such public crowd-sourced stories are “New York Story” or “Thanksgiving Story”, which comprise snaps that are aggregated for various public events, venues, etc. All snaps were posted between year 2016 and 2017, and do not contain raw images or other associated information (only textual captions and obfuscated visual descriptor features extracted from the pre-trained InceptionNet are available). We split the dataset into train (70%), validation (15%), and test sets (15%). The captions

`1802.07862:abstract:p0000:c0000` - Abstract; source characters 0:910.

> We introduce a new task called Multimodal Named Entity Recognition (MNER) for noisy user-generated data such as tweets or Snapchat captions, which comprise short text with accompanying images. These social media posts often come in inconsistent or incomplete syntax and lexical notations with very limited surrounding textual contexts, bringing significant challenges for NER. To this end, we create a new dataset for MNER called SnapCaptions (Snapchat image-caption pairs submitted to public and crowd-sourced stories with fully annotated named entities). We then build upon the state-of-the-art Bi-LSTM word/character based NER models with 1) a deep image network which incorporates relevant visual context to augment textual information, and 2) a generic modality-attention module which learns to attenuate irrelevant modalities while amplifying the most informative ones to extract contexts from, adaptive

`1802.07862:s0000:p0001:c0000` - Introduction; source characters 0:816.

> While many previous approaches BIBREF0 , BIBREF1 , BIBREF2 , BIBREF3 on NER have shown success for well-formed text in recognizing named entities via word context resolution (e.g. LSTM with word embeddings) combined with character-level features (e.g. CharLSTM/CNN), several additional challenges remain for recognizing named entities from extremely short and coarse text found in social media posts. For instance, short social media posts often do not provide enough textual contexts to resolve polysemous entities (e.g. “monopoly is da best ", where `monopoly' may refer to a board game (named entity) or a term in economics). In addition, noisy text includes a huge number of unknown tokens due to inconsistent lexical notations and frequent mentions of various newly trending entities (e.g. “xoxo Marshmelloooo "

Human correctness/refusal judgment: pending.

## 3. What kind of stylistic features are obtained?

Paper: `1701.05574`; question: `22732cb9476e521452bf0538f3fdb94cf3867651`; request: `9a9ce2d11de94d409a8189bac6c05eca`.
Saved status: **answered**. Human review: **pending**.

### Claim 1

The paper obtains stylistic patterns as part of the features used for sarcasm detection.

Citations: `1701.05574:s0001:p0001:c0000`

Human support: pending. Human note:

### Cited passages

`1701.05574:s0001:p0001:c0000` - Related Work; source characters 0:336.

> Computational linguists have previously addressed this problem using rule based and statistical techniques, that make use of : (a) Unigrams and Pragmatic features BIBREF0 , BIBREF1 , BIBREF2 , BIBREF3 (b) Stylistic patterns BIBREF4 and patterns related to situational disparity BIBREF5 and (c) Hastag interpretations BIBREF6 , BIBREF7 .

Human correctness/refusal judgment: pending.

## 4. Does their NER model learn NER from both text and images?

Paper: `1802.07862`; question: `adbf33c6144b2f5c40d0c6a328a92687a476f371`; request: `845bf2d49aff468db485258529f010f9`.
Saved status: **answered**. Human review: **pending**.

### Claim 1

The multimodal NER model learns named entity recognition by jointly using textual information (word and character embeddings) and visual information from the accompanying image.

Citations: `1802.07862:s0002:p0000:c0000`, `1802.07862:s0003:p0004:c0000`

Human support: pending. Human note:

### Cited passages

`1802.07862:s0002:p0000:c0000` - Proposed Methods; source characters 0:586.

> Figure FIGREF2 illustrates the proposed multimodal NER (MNER) model. First, we obtain word embeddings, character embeddings, and visual features (Section SECREF3 ). A Bi-LSTM-CRF model then takes as input a sequence of tokens, each of which comprises a word token, a character sequence, and an image, in their respective representation (Section SECREF4 ). At each decoding step, representations from each modality are combined via the modality attention module to produce an entity label for each token ( SECREF5 ). We formulate each component of the model in the following subsections.

`1802.07862:s0003:p0004:c0000` - Features; source characters 0:504.

> Incorporating this visual information onto the traditional NER system is an open challenge, and multiple approaches can be considered. For instance, one may provide visual contexts only as an initial input to decoder as in some encoder-decoder image captioning systems BIBREF26 . However, we empirically observe that an NER decoder which takes as input the visual embeddings at every decoding step (Section SECREF4 ), combined with the modality attention module (Section SECREF5 ), yields better results.

Human correctness/refusal judgment: pending.

## 5. What future possible improvements are listed?

Paper: `1912.10011`; question: `d915b401bb96c9f104a0353bef9254672e6f5a47`; request: `098c67a2117244daaab64cd5e78297d4`.
Saved status: **insufficient_evidence**. Human review: **pending**.

### Supplied passages

`1912.10011:s0016:p0001:c0000` - Results ::: Comparison w.r.t. baselines.; source characters 0:79.

> Specifically, regarding all baselines, we can outline the following statements.

`1912.10011:s0016:p0006:c0000` - Results ::: Comparison w.r.t. baselines.; source characters 0:436.

> We would also like to draw attention to the number of parameters used by those architectures. We note that our scenarios relies on a lower number of parameters (14 millions) compared to all baselines (ranging from 23 to 45 millions). This outlines the effectiveness in the design of our model relying on a structure encoding, in contrast to other approach that try to learn the structure of data/descriptions from a linearized encoding.

`1912.10011:s0018:p0000:c0000` - Acknowledgements; source characters 0:117.

> We would like to thank the H2020 project AI4EU (825619) which partially supports Laure Soulier and Patrick Gallinari.

`1912.10011:s0016:p0000:c0000` - Results ::: Comparison w.r.t. baselines.; source characters 0:833.

> From a general point of view, we can see from Table TABREF25 that our scenarios obtain significantly higher results in terms of BLEU over all models; our best model Hierarchical-k reaching $17.5$ vs. $16.5$ against the best baseline. This means that our models learns to generate fluent sequences of words, close to the gold descriptions, adequately picking up on domain lingo. Qualitative metrics are either better or on par with baselines. We show in Figure FIGREF29 a text generated by our best model, which can be directly compared to the gold description in Figure FIGREF1. Generation is fluent and contains domain-specific expressions. As reflected in Table TABREF25, the number of correct mentions (in green) outweights the number of incorrect mentions (in red). Please note that, as in previous work BIBREF28, BIBREF12, BIBRE

`1912.10011:s0010:p0004:c0000` - Experimental setup ::: Evaluation metrics ::: Information extraction-oriented metrics.; source characters 0:453.

> CS primarily targets the “what to say" aspect of evaluation, CO targets the “how to say it" aspect, and RG targets both. Note that for CS, CO, RG-% and BLEU metrics, higher is better; which is not true for RG-#. The IE system used in the experiments is able to extract an average of 17 factual records from gold descriptions. In order to mimic a human expert, a generative system should approach this number and not overload generation with brute facts.

Human correctness/refusal judgment: pending.

## 6. How many electrodes were used on the subject in EEG sessions?

Paper: `1904.04358`; question: `c7b6e6cb997de1660fd24d31759fe6bb21c7863f`; request: `b8b5e530c6ce4809b2854a3d621ccfba`.
Saved status: **insufficient_evidence**. Human review: **pending**.

### Supplied passages

`1904.04358:s0009:p0003:c0000` - Performance analysis and discussion; source characters 0:688.

> Next, we provide performance comparison of the proposed approach with the baseline methods for PHASE-TWO of our study (cross-validation experiment) in Table TABREF15 . Since the model encounters the unseen data of a new subject for testing, and given the high inter-subject variability of the EEG data, a reduction in the accuracy was expected. However, our network still managed to achieve an improvement of 18.91, 9.95, 67.15, 2.83 and 13.70 % over BIBREF17 . Besides, our best model shows more reliability compared to previous works: The standard deviation of our model's classification accuracy across all the tasks is reduced from 22.59% BIBREF17 and 17.52% BIBREF18 to a mere 5.41%.

`1904.04358:s0008:p0000:c0000` - Training and hyperparameter selection; source characters 0:571.

> We performed two sets of experiments with the single-trial EEG data. In PHASE-ONE, our goals was to identify the best architectures and hyperparameters for our networks with a reasonable number of runs. For PHASE-ONE, we randomly shuffled and divided the data (1913 signals from 14 individuals) into train (80%), development (10%) and test sets (10%). In PHASE-TWO, in order to perform a fair comparison with the previous methods reported on the same dataset, we perform a leave-one-subject out cross-validation experiment using the best settings we learn from PHASE-ONE.

`1904.04358:s0003:p0000:c0000` - Joint variability of electrodes; source characters 0:959.

> Multichannel EEG data is high dimensional multivariate time series data whose dimensionality depends on the number of electrodes. It is a major hurdle to optimally encode information from these EEG data into lower dimensional space. In fact, our investigation based on a development set (as we explain later) showed that well-known deep neural networks (e.g., fully connected networks such as convolutional neural networks, recurrent neural networks and autoencoders) fail to individually learn such complex feature representations from single-trial EEG data. Besides, we found that instead of using the raw multi-channel high-dimensional EEG requiring large training times and resource requirements, it is advantageous to first reduce its dimensionality by capturing the information transfer among the electrodes. Instead of the conventional approach of selecting a handful of channels as BIBREF17 , BIBREF18 , we address this by computing the channel cross-

`1904.04358:s0000:p0001:c0000` - Introduction; source characters 0:942.

> Among the various brain activity-monitoring modalities in BCI, electroencephalography (EEG) BIBREF5 , BIBREF6 has demonstrated promising potential to differentiate between various brain activities through measurement of related electric fields. EEG is non-invasive, portable, low cost, and provides satisfactory temporal resolution. This makes EEG suitable to realize BCI systems. EEG data, however, is challenging: these data are high dimensional, have poor SNR, and suffer from low spatial resolution and a multitude of artifacts. For these reasons, it is not particularly obvious how to decode the desired information from raw EEG signals. Although the area of BCI based speech intent recognition has received increasing attention among the research community in the past few years, most research has focused on classification of individual speech categories in terms of discrete vowels, phonemes and words BIBREF7 , BIBREF8 , BIBREF9 , BI

`1904.04358:s0003:p0000:c0002` - Joint variability of electrodes; source characters 1593:1876.

> hidden information than mere raw signals. This is essentially different than our previous work BIBREF16 where we extract per-channel 1-D covariance information and feed it to the networks. We present our sample 2-D EEG cross-covariance matrices (of two individuals) in Fig. FIGREF2 .

Human correctness/refusal judgment: pending.

## 7. Did they use a crowdsourcing platform?

Paper: `1908.05441`; question: `49764eee7fb523a6a28375cc699f5e0220b81766`; request: `3cabd3e0456a4c5999afda1890734eaf`.
Saved status: **insufficient_evidence**. Human review: **pending**.

### Supplied passages

`1908.05441:s0011:p0005:c0000` - Annotation; source characters 0:527.

> Interannotator Agreement: To increase quality and consistency, each annotator annotated the entire dataset of 7,787 questions. Two annotators were used, with the lead annotator possessing previous professional domain expertise. Annotation proceeded in a two-stage process, where in stage 1 annotators completed their annotation independently, and in stage 2 each of the questions where the annotators did not have complete agreement were manually resolved by the annotators, resulting in high-quality classification annotation.

`1908.05441:s0011:p0008:c0000` - Annotation; source characters 0:691.

> Annotators disagreed on 3441 (44.2%) of questions. Primary sources of disagreement before resolution included each annotator choosing a single category for questions requiring multiple labels (e.g. annotator 1 assigning a label of X, and annotator 2 assigning a label of Y, when the gold label was multilabel X, Y), which was observed in 18% of disagreements. Similarly, we observed annotators choosing similar labels but at different levels of specificity in the taxonomy (e.g. annotator 1 assigning a label of Matter INLINEFORM0 Changes of State INLINEFORM1 Boiling, where annotator 2 assigned Matter INLINEFORM2 Changes of State), which occurred in 12% of disagreements before resolution.

`1908.05441:s0006:p0009:c0000` - Question Answering with QC Labels; source characters 0:729.

> Though initial raw interannotator agreement was measured at INLINEFORM0 , to maximize the quality of the annotation the annotators performed a second pass where all disagreements were manually resolved. Table TABREF30 shows question classification performance of the BERT-QC model at 57.8% P@1, meaning 42.2% of the predicted labels were different than the gold labels. The question classification error analysis in Table TABREF20 found that of these 42.2% of errorful predictions, 10% of errors (4.2% of total labels) were caused by the gold labels being incorrect. This allows us to estimate that the overall quality of the annotation (the proportion of questions that have a correct human authored label) is approximately 96%.

`1908.05441:s0007:p0002:c0000` - Automating Error Analyses with QC; source characters 0:578.

> While this analysis is shown at an intermediate (L2) level of specificity for space, more detailed analyses are possible. For example, overall QA performance on Scientific Inference questions is near average (47%), but increasing granularity to L3 we observe that questions addressing Experiment Design or Making Inferences – challenging questions even for humans – perform poorly (33% and 20%) when answered by the QA system. This allows a system designer to intelligently target problem-specific knowledge resources and inference methods to address deficits in specific areas.

`1908.05441:s0010:p0000:c0000` - Acknowledgements; source characters 0:275.

> The authors wish to thank Elizabeth Wainwright and Stephen Marmorstein for piloting an earlier version of the question classification annotation. We thank the Allen Insitute for Artificial Intelligence and National Science Founation (NSF 1815948 to PJ) for funding this work.

Human correctness/refusal judgment: pending.

## 8. What dataset was used?

Paper: `1910.09982`; question: `df5a4505edccc0ee11349ed6e7958cf6b84c9ed4`; request: `d3d43b2695a145abbbace9a005115851`.
Saved status: **answered**. Human review: **pending**.

### Claim 1

The shared task used a corpus that was annotated by A Data Pro, a company that performs high-quality manual annotations.

Citations: `1910.09982:s0035:p0001:c0000`

Human support: pending. Human note:

### Cited passages

`1910.09982:s0035:p0001:c0000` - Acknowledgments; source characters 0:109.

> The corpus for the task was annotated by A Data Pro, a company that performs high-quality manual annotations.

Human correctness/refusal judgment: pending.

## 9. Which real-world datasets are used?

Paper: `1912.00667`; question: `3941401a182a3d6234894a5c8a75d48c6116c45c`; request: `50e7f6a306004199aeeded02a26ddc4b`.
Saved status: **answered**. Human review: **pending**.

### Claim 1

The study uses two real‑world datasets: one for the CyberAttack event category and one for the PoliticianDeath event category.

Citations: `1912.00667:s0007:p0000:c0000`, `1912.00667:s0007:p0000:c0001`

Human support: pending. Human note:

### Cited passages

`1912.00667:s0007:p0000:c0000` - Experiments and Results ::: Experimental Setup; source characters 0:907.

> Datasets. We perform our experiments with two predetermined event categories: cyber security (CyberAttack) and death of politicians (PoliticianDeath). These event categories are chosen as they are representative of important event types that are of interest to many governments and companies. The need to create our own dataset was motivated by the lack of public datasets for event detection on microposts. The few available datasets do not suit our requirements. For example, the publicly available Events-2012 Twitter dataset BIBREF20 contains generic event descriptions such as Politics, Sports, Culture etc. Our work targets more specific event categories BIBREF21. Following previous studies BIBREF1, we collect event-related microposts from Twitter using 11 and 8 seed events (see Section SECREF2) for CyberAttack and PoliticianDeath, respectively. Unlabeled microposts are collected by using the key

`1912.00667:s0007:p0000:c0001` - Experiments and Results ::: Experimental Setup; source characters 783:1232.

> (see Section SECREF2) for CyberAttack and PoliticianDeath, respectively. Unlabeled microposts are collected by using the keyword `hack' for CyberAttack, while for PoliticianDeath, we use a set of keywords related to `politician' and `death' (such as `bureaucrat', `dead' etc.) For each dataset, we randomly select 500 tweets from the unlabeled subset and manually label them for evaluation. Table TABREF25 shows key statistics from our two datasets.

Human correctness/refusal judgment: pending.

## 10. Which qualitative metric are used for evaluation?

Paper: `1912.10011`; question: `79a44a68bb57b375d8a57a0a7f522d33476d9f33`; request: `e1d70f2a681a42ea8577a7705177f5c6`.
Saved status: **answered**. Human review: **pending**.

### Claim 1

The qualitative evaluation metrics used are CS (Content Selection), CO (Content Ordering), and RG (Reference Generation).

Citations: `1912.10011:s0010:p0000:c0000`, `1912.10011:s0010:p0004:c0000`

Human support: pending. Human note:

### Cited passages

`1912.10011:s0010:p0000:c0000` - Experimental setup ::: Evaluation metrics ::: Information extraction-oriented metrics.; source characters 0:712.

> These metrics estimate the ability of our model to integrate elements from the table in its descriptions. Particularly, they compare the gold and generated descriptions and measure to what extent the extracted relations are aligned or differ. To do so, we follow the protocol presented in BIBREF10. First, we apply an information extraction (IE) system trained on labeled relations from the gold descriptions of the RotoWire train dataset. Entity-value pairs are extracted from the descriptions. For example, in the sentence Isaiah Thomas led the team in scoring, totaling 23 points [...]., an IE tool will extract the pair (Isaiah Thomas, 23, PTS). Second, we compute three metrics on the extracted information:

`1912.10011:s0010:p0004:c0000` - Experimental setup ::: Evaluation metrics ::: Information extraction-oriented metrics.; source characters 0:453.

> CS primarily targets the “what to say" aspect of evaluation, CO targets the “how to say it" aspect, and RG targets both. Note that for CS, CO, RG-% and BLEU metrics, higher is better; which is not true for RG-#. The IE system used in the experiments is able to extract an average of 17 factual records from gold descriptions. In order to mimic a human expert, a generative system should approach this number and not overload generation with brute facts.

Human correctness/refusal judgment: pending.

## 11. what previous RNN models do they compare with?

Paper: `1808.09029`; question: `6aaf12505add25dd133c7b0dafe8f4fe966d1f1d`; request: `2756ef114ab34b9cbda6aa3cdbe507ad`.
Saved status: **answered**. Human review: **pending**.

### Claim 1

The paper compares its Pyramidal Recurrent Unit (PRU) against the Long Short-Term Memory (LSTM) model.

Citations: `1808.09029:s0010:p0003:c0000`

Human support: pending. Human note:

### Cited passages

`1808.09029:s0010:p0003:c0000` - Ablation studies; source characters 0:617.

> Fixed INLINEFORM0 and variable INLINEFORM1 : When we vary the value of INLINEFORM2 at fixed number of pyramidal levels INLINEFORM3 , the total number of recurrent unit parameters decreases significantly with a minimal impact on the perplexity. For example, PRUs with INLINEFORM4 and INLINEFORM5 learns 77% fewer recurrent unit parameters while its perplexity (lower is better) increases by about 12% in comparison to LSTMs. Moreover, the decrease in number of parameters at higher value of INLINEFORM6 enables PRUs to learn the representations in high dimensional space with better generalizability (Table TABREF23 ).

Human correctness/refusal judgment: pending.

## 12. What was their system's performance?

Paper: `1706.01875`; question: `bdf93053b1b9b0a21f77ed370cf4d5a10df70e3e`; request: `baf9bef09a584646a076ba7ac4d17b2b`.
Saved status: **answered**. Human review: **pending**.

### Claim 1

The classifier achieved an accuracy of 89.6% and an F1‑score of 89.2% on the holdout set.

Citations: `1706.01875:s0004:p0002:c0000`

Human support: pending. Human note:

### Cited passages

`1706.01875:s0004:p0002:c0000` - Classifier evaluation; source characters 0:445.

> Real-world classifier performance. To evaluate real-world performance of our selected classifier (i.e., performance in the absence of model and parameter bias), we perform classification of the holdout set. On this set, our classifier had an accuracy and F1-score of 89.6% and 89.2%, respectively. These results show that in addition to superior accuracy during training and validation, our chosen classifier is also robust against over-fitting.

Human correctness/refusal judgment: pending.

## 13. Does the experiments focus on a specific domain?

Paper: `1703.04001`; question: `4e1a67f8dc68b55a5ce18e6cd385ae9ab90d891f`; request: `442bc641773a4164aaed794e519fa095`.
Saved status: **insufficient_evidence**. Human review: **pending**.

### Supplied passages

`1703.04001:s0002:p0003:c0000` - Linguistic activities on Quora; source characters 0:27.

> Psycholinguistic analysis:

`1703.04001:s0000:p0001:c0000` - Introduction; source characters 0:954.

> Characterization of the questions based on question quality requires expert human interventions often judging if a question would remain open based on factors like if it is subjective, controversial, open-ended, vague/imprecise, ill-formed, off-topic, ambiguous, uninteresting etc. Collecting judgment data for thousands of question posts is a very expensive process. Therefore, such an experiment can be done only for a small set of questions and it would be practically impossible to scale it up for the entire collection of posts on the Q&A site. In this work, we show that appropriate quantification of various linguistic activities can naturally correspond to many of the judgment factors mentioned above (see table 2 for a collection of examples). These quantities encoding such linguistic activities can be easily measured for each question post and thus helps us to have an alternative mechanism to characterize the answerability on the Q&A site.

`1703.04001:s0000:p0002:c0000` - Introduction; source characters 0:616.

> There are several research works done in Q&A focusing on content of posts. BIBREF0 exploit community feedback to identify high quality content on Yahoo! Answers. BIBREF1 use textual features to predict answer quality on Yahoo! Answers. BIBREF2 , investigate predictors of answer quality through a comparative, controlled field study of user responses. BIBREF3 study the problem of how long questions remain unanswered. BIBREF4 propose a prediction model on how many answers a question shall receive. BIBREF5 analyze and predict unanswered questions on Yahoo Answers. BIBREF6 study question quality in Yahoo! Answers.

`1703.04001:abstract:p0000:c0001` - Abstract; source characters 746:919.

> for an accuracy of 74.18%. We also compare our method with some of the similar works (Dror et al., Yang et al.) achieving a maximum improvement of ~39% in terms of accuracy.

`1703.04001:s0003:p0002:c0000` - Prediction model; source characters 0:273.

> The content and way of posing a question is important to attract answers. We have observed in the previous section that these linguistic as well as psycholinguistic aspects of the question asker are discriminatory factors. For the prediction, we use the following features:

Human correctness/refusal judgment: pending.

## 14. What did the best systems use for their model?

Paper: `1907.03187`; question: `b7c3f3942a07c118e57130bc4c3ec4adc431d725`; request: `8382d1377769466982e4c7ae82302df6`.
Saved status: **answered**. Human review: **pending**.

### Claim 1

The best systems used a QRNN-based language model with about 60 million trainable parameters.

Citations: `1907.03187:s0006:p0000:c0001`

Human support: pending. Human note:

### Claim 2

They tokenized the data with sentencepiece BIBREF4 using a byte‑pair encoding (BPE) vocabulary of 30,000 sub‑word units.

Citations: `1907.03187:s0005:p0000:c0000`

Human support: pending. Human note:

### Cited passages

`1907.03187:s0006:p0000:c0001` - LM Training and Fine-tuning; source characters 611:905.

> We performed some simple tests with LSTM units and a Transformer Language model, finding all models were similar in performance during LM training. We thus chose to use QRNN units due to improved training speed compared to the alternatives. This model has about 60 million trainable parameters.

`1907.03187:s0005:p0000:c0000` - Tokenization; source characters 0:318.

> We used sentencepiece BIBREF4 to parse into sub-word units and reduce the possible out-of-vocabulary terms in the data set. We selected a vocab size of 30,000 and used the byte-pair encoding (BPE) model. To our knowledge this is the first time that the BPE toenization has been used with ULMFiT in a competition model.

Human correctness/refusal judgment: pending.

## 15. What is NER?

Paper: `1705.05437`; question: `cf874cd9023d901e10aa8664b813d32501e7e4d2`; request: `6cd69634d85444a8923f9e8ed9310793`.
Saved status: **answered**. Human review: **pending**.

### Claim 1

Named Entity Recognition (NER) in the Biomedical domain usually includes recognition of entities such as proteins, genes, diseases, treatments, drugs, etc.

Citations: `1705.05437:s0001:p0000:c0000`

Human support: pending. Human note:

### Cited passages

`1705.05437:s0001:p0000:c0000` - Named Entity Recognition and Fact Extraction; source characters 0:368.

> Named Entity Recognition (NER) in the Biomedical domain usually includes recognition of entities such as proteins, genes, diseases, treatments, drugs, etc. Fact extraction involves extraction of Named Entities from a corpus, usually given a certain ontology. When compared to NER in the domain of general text, the biomedical domain has some characteristic challenges:

Human correctness/refusal judgment: pending.

## 16. Do they inspect their model to see if their model learned to associate image parts with words related to entities?

Paper: `1802.07862`; question: `7cd22ca9e107d2b13a7cc94252aaa9007976b338`; request: `a2110378a53247eab91a0f58a207a57c`.
Saved status: **insufficient_evidence**. Human review: **pending**.

### Supplied passages

`1802.07862:s0008:p0005:c0000` - Results: SnapCaptions Dataset; source characters 0:948.

> For the image-aided model (W+C+V; upper row in Figure FIGREF19 ), we confirm that the modality attention successfully attenuates irrelevant signals (selfies, etc.) and amplifies relevant modality-based contexts in prediction of a given token. In the example of “disney word essential = coffee" with visual tags selfie, phone, person, the modality attention successfully attenuates distracting visual signals and focuses on textual modalities, consequently making correct predictions. The named entities in the examples of “Beautiful night atop The Space Needle" and “Splash Mountain" are challenging to predict because they are composed of common nouns (space, needle, splash, mountain), and thus they often need additional contexts to correctly predict. In the training data, visual contexts make stronger indicators for these named entities (space needle, splash mountain), and the modality attention module successfully attends more to stronger

`1802.07862:s0008:p0003:c0000` - Results: SnapCaptions Dataset; source characters 0:877.

> Error Analysis: Table TABREF17 shows example cases where incorporation of visual contexts affects prediction of named entities. For example, the token `curry' in the caption “The curry's " is polysemous and may refer to either a type of food or a famous basketball player `Stephen Curry', and the surrounding textual contexts do not provide enough information to disambiguate it. On the other hand, visual contexts (visual tags: `parade', `urban area', ...) provide similarities to the token's distributional semantics from other training examples (snaps from “NBA Championship Parade Story"), and thus the model successfully predicts the token as a named entity. Similarly, while the text-only model erroneously predicts `Apple' in the caption “Grandma w dat lit Apple Crisp" as an organization (Apple Inc.), the visual contexts (describing objects related to food) help disam

`1802.07862:s0008:p0007:c0000` - Results: SnapCaptions Dataset; source characters 0:390.

> Figure FIGREF19 (b) shows the cases where the modality attention led to incorrect predictions. For example, the model predicts missing tokens HUUUGE and Shampooer incorrectly as named entities by amplifying misleading character-based contexts (capitalized first letters) or visual contexts (concert scenes, associated contexts of which often include named entities in the training dataset).

`1802.07862:s0008:p0003:c0001` - Results: SnapCaptions Dataset; source characters 737:1358.

> caption “Grandma w dat lit Apple Crisp" as an organization (Apple Inc.), the visual contexts (describing objects related to food) help disambiguate the token, making the model predict it correctly as a non-named entity (a fruit). Trending entities (musicians or DJs such as `CID', `Duke Dumont', `Marshmello', etc.) are also recognized correctly with strengthened contexts from visual information (describing concert scenes) despite lack of surrounding textual contexts. A few cases where visual contexts harmed the performance mostly include visual tags that are unrelated to a token or its surrounding textual contexts.

`1802.07862:s0001:p0004:c0000` - Related Work; source characters 0:127.

> To the best of our knowledge, our approach is the first work to incorporate visual contexts for named entity recognition tasks.

Human correctness/refusal judgment: pending.

## 17. Why are current ELS's not sufficiently effective?

Paper: `1806.05504`; question: `ef7212075e80bf35b7889dc8dd52fcbae0d1400a`; request: `6962d5a79faa43b9a332d923237bb57e`.
Saved status: **answered**. Human review: **pending**.

### Claim 1

Current entity linking systems (ELS) suffer from low precision, leading to many incorrect and irrelevant entities being extracted.

Citations: `1806.05504:s0003:p0000:c0000`, `1806.05504:s0003:p0002:c0001`

Human support: pending. Human note:

### Claim 2

The extracted entities are often ambiguous and too coarse, which further degrades their usefulness for downstream tasks such as summarization.

Citations: `1806.05504:s0003:p0000:c0000`

Human support: pending. Human note:

### Cited passages

`1806.05504:s0003:p0000:c0000` - Possible issues; source characters 0:239.

> Despite its usefulness, linked entities extracted from ELS's have issues because of low precision rates BIBREF11 and design challenges in training datasets BIBREF12 . These issues can be summarized into two parts: ambiguity and coarseness.

`1806.05504:s0003:p0002:c0001` - Possible issues; source characters 704:852.

> $30.0\%$ , and $26.9\%$ are tagged with A, B, C, and D, respectively, which shows that there is a large amount of incorrect and irrelevant entities.

Human correctness/refusal judgment: pending.

## 18. What news article sources are used?

Paper: `1703.10344`; question: `61a9ea36ddc37c60d1a51dabcfff9445a2225725`; request: `fd4b4677811c4fa08a2373dfbd675bba`.
Saved status: **insufficient_evidence**. Human review: **pending**.

### Supplied passages

`1703.10344:s0000:p0006:c0000` - Introduction; source characters 0:480.

> We evaluate the proposed approach on a news corpus consisting of 351,982 articles crawled from the news external references in Wikipedia from 73,734 entity pages. Given the Wikipedia snapshot at a given year (in our case [2009-2014]), we suggest news articles that might be cited in the coming years. The existing news references in the entity pages along with their reference date act as our ground-truth to evaluate our approach. In summary, we make the following contributions.

`1703.10344:s0008:p0002:c0000` - Datasets; source characters 0:449.

> News Articles. We extract all news references from the collected Wikipedia entity pages. The extracted news references are associated with the sections in which they appear. In total there were INLINEFORM0 news references, and after crawling we end up with INLINEFORM1 successfully crawled news articles. The details of the news article distribution, and the number of entities and sections from which they are referred are shown in Table TABREF44 .

`1703.10344:s0000:p0004:c0000` - Introduction; source characters 0:1021.

> We identify four properties of good news recommendations: salience, relative authority, novelty and placement. First, we need to identify the most salient entities in a news article. This is done to avoid pollution of entity pages with only marginally related news. Second, we need to determine whether the news is important to the entity as only the most relevant news should be added to a precise reference work. To do this, we compute the relative authority of all entities in the news article: we call an entity more authoritative than another if it is more popular or noteworthy in the real world. Entities with very high authority have many news items associated with them and only the most relevant of these should be included in Wikipedia whereas for entities of lower authority the threshold for inclusion of a news article will be lower. Third, a good recommendation should be able to identify novel news by minimizing redundancy coming from multiple news articles. Finally, addition of facts is facilitated if

`1703.10344:s0012:p0001:c0000` - Conclusion and Future Work; source characters 0:292.

> In the future, we will enhance our work by extracting facts from the suggested news articles. Results suggest that the news content cited in entity pages comes from the first paragraphs. However, challenging task such as the canonicalization and chronological ordering of facts, still remain.

`1703.10344:s0005:p0008:c0000` - Article–Entity Placement; source characters 0:901.

> Relative Authority. In this case, we consider the comparative relevance of the news article to the different entities occurring in it. As an example, let us consider the meeting of the Sudanese bishop Elias Taban with Hillary Clinton. Both entities are salient for the meeting. However, in Taban's Wikipedia page, this meeting is discussed prominently with a corresponding news reference, whereas in Hillary Clinton's Wikipedia page it is not reported at all. We believe this is not just an omission in Clinton's page but mirrors the fact that for the lesser known Taban the meeting is big news whereas for the more famous Clinton these kind of meetings are a regular occurrence, not all of which can be reported in what is supposed to be a selection of the most important events for her. Therefore, if two entities co-occur, the news is more relevant for the entity with the lower a priori authority.

Human correctness/refusal judgment: pending.

## 19. What baseline model is used?

Paper: `1703.10344`; question: `2ee715c7c6289669f11a79743a6b2b696073805d`; request: `c593ee26219242c984559eeafda35015`.
Saved status: **answered**. Human review: **pending**.

### Claim 1

The first baseline model uses only the salience-based features by Dunietz and Gillick.

Citations: `1703.10344:s0005:p0020:c0000`

Human support: pending. Human note:

### Cited passages

`1703.10344:s0005:p0020:c0000` - Article–Entity Placement; source characters 0:94.

> B1. The first baseline uses only the salience-based features by Dunietz and Gillick BIBREF11 .

Human correctness/refusal judgment: pending.

## 20. How were crowd workers instructed to identify important elements in large document collections?

Paper: `1704.04452`; question: `e9cfbfdf30e48cffdeca58d4ac6fdd66a8b27d7a`; request: `100a33ab055043a095ea9a9d2776f33b`.
Saved status: **answered**. Human review: **pending**.

### Claim 1

Crowd workers were instructed to judge the importance of individual propositions by scoring each proposition’s relevance to the document cluster, using only a brief description of the cluster’s topic and the propositions themselves, without viewing the full documents.

Citations: `1704.04452:s0004:p0000:c0000`

Human support: pending. Human note:

### Cited passages

`1704.04452:s0004:p0000:c0000` - Task Design; source characters 0:588.

> We break down the task of importance annotation to the level of single propositions. The goal of our crowdsourcing scheme is to obtain a score for each proposition indicating its importance in a document cluster, such that a ranking according to the score would reveal what is most important and should be included in a summary. In contrast to other work, we do not show the documents to the workers at all, but provide only a description of the document cluster's topic along with the propositions. This ensures that tasks are small, simple and can be done quickly (see Figure FIGREF4 ).

Human correctness/refusal judgment: pending.

## 21. What is the baseline?

Paper: `1912.04961`; question: `99e78c390932594bd833be0f5c890af5c605d808`; request: `b482a42d70c44ca993a857053b41a7a5`.
Saved status: **answered**. Human review: **pending**.

### Claim 1

The baseline models used in the experiments are QA PGNet and Multi-decoder QA PGNet with lookup table embedding.

Citations: `1912.04961:s0009:p0000:c0000`

Human support: pending. Human note:

### Cited passages

`1912.04961:s0009:p0000:c0000` - Experiments ::: Model variations; source characters 0:162.

> We consider QA PGNet and Multi-decoder QA PGNet with lookup table embedding as baseline models and improve on the baselines with other variations described below.

Human correctness/refusal judgment: pending.

## 22. How do they demonstrate that this type of EEG has discriminative information about the intended articulatory movements responsible for speech?

Paper: `1904.04358`; question: `7ae38f51243cb80b16a1df14872b72a1f8a2048f`; request: `7302709489054025a228182175e5ecf1`.
Saved status: **insufficient_evidence**. Human review: **pending**.

### Supplied passages

`1904.04358:s0000:p0002:c0000` - Introduction; source characters 0:950.

> Production of articulatory speech is an extremely complicated process, thereby rendering understanding of the discriminative EEG manifold corresponding to imagined speech highly challenging. As a result, most of the existing approaches failed to achieve satisfactory accuracy on decoding speech tokens from the speech imagery EEG data. Perhaps, for these reasons, very little work has been devoted to relating the brain signals to the underlying articulation. The few exceptions include BIBREF17 , BIBREF18 . In BIBREF17 , Zhao et al. used manually handcrafted features from EEG data, combined with speech audio and facial features to achieve classification of the phonological categories varying based on the articulatory steps. However, the imagined speech classification accuracy based on EEG data alone, as reported in BIBREF17 , BIBREF18 , are not satisfactory in terms of accuracy and reliability. We now turn to describing our proposed models.

`1904.04358:s0007:p0000:c0000` - Dataset; source characters 0:788.

> We evaluate our model on a publicly available dataset, KARA ONE BIBREF17 , composed of multimodal data for stimulus-based, imagined and articulated speech state corresponding to 7 phonemic/syllabic ( /iy/, /piy/, /tiy/, /diy/, /uw/, /m/, /n/ ) as well as 4 words(pat, pot, knew and gnaw). The dataset consists of 14 participants, with each prompt presented 11 times to each individual. Since our intention is to classify the phonological categories from human thoughts, we discard the facial and audio information and only consider the EEG data corresponding to imagined speech. It is noteworthy that given the mixed nature of EEG signals, it is reportedly challenging to attain a pairwise EEG-phoneme mapping BIBREF18 . In order to explore the problem space, we thus specifically target

`1904.04358:s0000:p0001:c0000` - Introduction; source characters 0:942.

> Among the various brain activity-monitoring modalities in BCI, electroencephalography (EEG) BIBREF5 , BIBREF6 has demonstrated promising potential to differentiate between various brain activities through measurement of related electric fields. EEG is non-invasive, portable, low cost, and provides satisfactory temporal resolution. This makes EEG suitable to realize BCI systems. EEG data, however, is challenging: these data are high dimensional, have poor SNR, and suffer from low spatial resolution and a multitude of artifacts. For these reasons, it is not particularly obvious how to decode the desired information from raw EEG signals. Although the area of BCI based speech intent recognition has received increasing attention among the research community in the past few years, most research has focused on classification of individual speech categories in terms of discrete vowels, phonemes and words BIBREF7 , BIBREF8 , BIBREF9 , BI

`1904.04358:s0000:p0001:c0001` - Introduction; source characters 812:1403.

> on classification of individual speech categories in terms of discrete vowels, phonemes and words BIBREF7 , BIBREF8 , BIBREF9 , BIBREF10 , BIBREF11 , BIBREF12 , BIBREF13 , BIBREF14 , BIBREF15 . This includes categorization of imagined EEG signal into binary vowel categories like /a/, /u/ and rest BIBREF7 , BIBREF8 , BIBREF9 ; binary syllable classes like /ba/ and /ku/ BIBREF1 , BIBREF10 , BIBREF11 , BIBREF12 ; a handful of control words like 'up', 'down', 'left', 'right' and 'select' BIBREF15 or others like 'water', 'help', 'thanks', 'food', 'stop' BIBREF13 , Chinese characters BIBREF

`1904.04358:s0001:p0000:c0000` - Proposed Framework; source characters 0:763.

> Cognitive learning process underlying articulatory speech production involves incorporation of intermediate feedback loops and utilization of past information stored in the form of memory as well as hierarchical combination of several feature extractors. To this end, we develop our mixed neural network architecture composed of three supervised and a single unsupervised learning step, discussed in the next subsections and shown in Fig. FIGREF1 . We formulate the problem of categorizing EEG data based on speech imagery as a non-linear mapping INLINEFORM0 of a multivariate time-series input sequence INLINEFORM1 to fixed output INLINEFORM2 , i.e, mathematically INLINEFORM3 : INLINEFORM4 , where c and t denote the EEG channels and time instants respectively.

Human correctness/refusal judgment: pending.

## 23. How large is their MNER SnapCaptions dataset?

Paper: `1802.07862`; question: `1591068b747c94f45b948e12edafe74b5e721047`; request: `2e33bfacc8d74482b16f2964c00968fd`.
Saved status: **answered**. Human review: **pending**.

### Claim 1

The SnapCaptions dataset contains 10,000 user-generated image and textual caption pairs.

Citations: `1802.07862:s0006:p0000:c0000`

Human support: pending. Human note:

### Cited passages

`1802.07862:s0006:p0000:c0000` - SnapCaptions Dataset; source characters 0:859.

> The SnapCaptions dataset is composed of 10K user-generated image (snap) and textual caption pairs where named entities in captions are manually labeled by expert human annotators (entity types: PER, LOC, ORG, MISC). These captions are collected exclusively from snaps submitted to public and crowd-sourced stories (aka Snapchat Live Stories or Our Stories). Examples of such public crowd-sourced stories are “New York Story” or “Thanksgiving Story”, which comprise snaps that are aggregated for various public events, venues, etc. All snaps were posted between year 2016 and 2017, and do not contain raw images or other associated information (only textual captions and obfuscated visual descriptor features extracted from the pre-trained InceptionNet are available). We split the dataset into train (70%), validation (15%), and test sets (15%). The captions

Human correctness/refusal judgment: pending.

## 24. How did they extend LAMA evaluation framework to focus on negation?

Paper: `1911.03343`; question: `78292bc57ee68fdb93ed45430d80acca25a9e916`; request: `dff1a51ba2de4fe584c7a7cf7e50ee8b`.
Saved status: **answered**. Human review: **pending**.

### Claim 1

They extended the LAMA evaluation framework by creating a new dataset called negated LAMA, which is obtained by inserting negation elements (e.g., “not”) into the original LAMA cloze statements (e.g., “The theory of relativity was not developed by [MASK].”).

Citations: `1911.03343:s0000:p0002:c0000`

Human support: pending. Human note:

### Claim 2

In their experiments they query pretrained language models with both the original LAMA statements and the corresponding negated statements, and then compare the predictions in terms of rank correlation and overlap of top predictions.

Citations: `1911.03343:s0000:p0002:c0000`

Human support: pending. Human note:

### Cited passages

`1911.03343:s0000:p0002:c0000` - Introduction; source characters 0:881.

> This work analyzes the understanding of pretrained language models of factual and commonsense knowledge stored in negated statements. To this end, we introduce the negated LAMA dataset. We construct it by simply inserting negation elements (e.g., “not”) in LAMA cloze statement (e.g., “The theory of relativity was not developed by [MASK].”). In our experiments, we query the pretrained language models with both original LAMA and negated LAMA statements and compare their predictions in terms of rank correlation and overlap of top predictions. We find that the predicted filler words often have high overlap. Thus, negating a cloze statement does not change the predictions in many cases – but of course it should as our example “birds can fly” vs. “birds cannot fly” shows. We identify and analyze a subset of cloze statements where predictions are different. We find that BERT

Human correctness/refusal judgment: pending.

## 25. what data did they use?

Paper: `1808.09029`; question: `7bd6a6ec230e1efb27d691762cc0674237dc7967`; request: `e25f2a1be4d24f79b964bbd23e14edd8`.
Saved status: **answered**. Human review: **pending**.

### Claim 1

The authors used the Penn Treebank (PTB) dataset and the WikiText-2 (WT-2) dataset for evaluation.

Citations: `1808.09029:s0007:p0000:c0000`

Human support: pending. Human note:

### Cited passages

`1808.09029:s0007:p0000:c0000` - Set-up; source characters 0:244.

> Following recent works, we compare on two widely used datasets, the Penn Treebank (PTB) BIBREF28 as prepared by BIBREF29 and WikiText2 (WT-2) BIBREF20 . For both datasets, we follow the same training, validation, and test splits as in BIBREF0 .

Human correctness/refusal judgment: pending.

## 26. Do the answered questions measure for the usefulness of the answer?

Paper: `1703.04001`; question: `9af3142630b350c93875441e1e1767312df76d17`; request: `7475011f72ed4ccc96b23d12692c6a32`.
Saved status: **insufficient_evidence**. Human review: **pending**.

### Supplied passages

`1703.04001:abstract:p0000:c0000` - Abstract; source characters 0:858.

> Quora is one of the most popular community Q&A sites of recent times. However, many question posts on this Q&A site often do not get answered. In this paper, we quantify various linguistic activities that discriminates an answered question from an unanswered one. Our central finding is that the way users use language while writing the question text can be a very effective means to characterize answerability. This characterization helps us to predict early if a question remaining unanswered for a specific time period t will eventually be answered or not and achieve an accuracy of 76.26% (t = 1 month) and 68.33% (t = 3 months). Notably, features representing the language use patterns of the users are most discriminative and alone account for an accuracy of 74.18%. We also compare our method with some of the similar works (Dror et al., Yang et al.)

`1703.04001:s0002:p0006:c0000` - Linguistic activities on Quora; source characters 0:390.

> In table 2 , we show a collection of examples of open questions to illustrate that many of the above quantities based on the linguistic activities described in this section naturally correspond to the factors that human judges consider responsible for a question remaining unanswered. This is one of the prime reasons why these quantities qualify as appropriate indicators of answerability.

`1703.04001:s0000:p0002:c0000` - Introduction; source characters 0:616.

> There are several research works done in Q&A focusing on content of posts. BIBREF0 exploit community feedback to identify high quality content on Yahoo! Answers. BIBREF1 use textual features to predict answer quality on Yahoo! Answers. BIBREF2 , investigate predictors of answer quality through a comparative, controlled field study of user responses. BIBREF3 study the problem of how long questions remain unanswered. BIBREF4 propose a prediction model on how many answers a question shall receive. BIBREF5 analyze and predict unanswered questions on Yahoo Answers. BIBREF6 study question quality in Yahoo! Answers.

`1703.04001:s0000:p0001:c0000` - Introduction; source characters 0:954.

> Characterization of the questions based on question quality requires expert human interventions often judging if a question would remain open based on factors like if it is subjective, controversial, open-ended, vague/imprecise, ill-formed, off-topic, ambiguous, uninteresting etc. Collecting judgment data for thousands of question posts is a very expensive process. Therefore, such an experiment can be done only for a small set of questions and it would be practically impossible to scale it up for the entire collection of posts on the Q&A site. In this work, we show that appropriate quantification of various linguistic activities can naturally correspond to many of the judgment factors mentioned above (see table 2 for a collection of examples). These quantities encoding such linguistic activities can be easily measured for each question post and thus helps us to have an alternative mechanism to characterize the answerability on the Q&A site.

`1703.04001:s0000:p0000:c0001` - Introduction; source characters 762:1722.

> , Yahoo! Answers etc. and these are some of the prime reasons behind its popularity in recent times. Quality question posting and getting them answered are the key objectives of any Q&A site. In this study we focus on the answerability of questions on Quora, i.e., whether a posted question shall eventually get answered. In Quora, the questions with no answers are referred to as “open questions”. These open questions need to be studied separately to understand the reason behind their not being answered or to be precise, are there any characteristic differences between `open' questions and the answered ones. For example, the question “What are the most promising advances in the treatment of traumatic brain injuries?” was posted on Quora on 23rd June, 2011 and got its first answer after almost 2 years on 22nd April, 2013. The reason that this question remained open so long might be the hardness of answering it and the lack of visibility and experts

Human correctness/refusal judgment: pending.

## 27. What are the three regularization terms?

Paper: `1503.00841`; question: `6becff2967fe7c5256fe0b00231765be5b9db9f1`; request: `5433c4e789414a38917c0d4720486e10`.
Saved status: **answered**. Human review: **pending**.

### Claim 1

A regularization term associated with neutral features

Citations: `1503.00841:s0000:p0005:c0000`

Human support: pending. Human note:

### Claim 2

The maximum entropy of class distribution regularization term

Citations: `1503.00841:s0000:p0005:c0000`

Human support: pending. Human note:

### Claim 3

The KL divergence between reference and predicted class distribution regularization term

Citations: `1503.00841:s0000:p0005:c0000`

Human support: pending. Human note:

### Cited passages

`1503.00841:s0000:p0005:c0000` - Introduction; source characters 0:570.

> More specifically, we explore three regularization terms to address the problem: (1) a regularization term associated with neutral features; (2) the maximum entropy of class distribution regularization term; and (3) the KL divergence between reference and predicted class distribution. For the first manner, we simply use the most common features as neutral features and assume the neutral features are distributed uniformly over class labels. For the second and third one, we assume we have some knowledge about the class distribution which will be detailed soon later.

Human correctness/refusal judgment: pending.

## 28. How do they obtain psychological dimensions of people?

Paper: `1612.06685`; question: `07d15501a599bae7eb4a9ead63e9df3d55b3dc35`; request: `d29ed87681504822a2ce5ebf6c956394`.
Saved status: **answered**. Human review: **pending**.

### Claim 1

They obtain psychological dimensions by mapping the language used in blogs to psycholinguistic word categories from lexical resources such as Linguistic Inquiry and Word Count (LIWC).

Citations: `1612.06685:s0005:p0001:c0000`

Human support: pending. Human note:

### Cited passages

`1612.06685:s0005:p0001:c0000` - Psycholinguistic and Semantic Maps; source characters 0:836.

> LIWC. In addition to individual words, we can also create maps for word categories that reflect a certain psycholinguistic or semantic property. Several lexical resources, such as Roget or Linguistic Inquiry and Word Count BIBREF9 , group words into categories. Examples of such categories are Money, which includes words such as remuneration, dollar, and payment; or Positive feelings with words such as happy, cheerful, and celebration. Using the distribution of the individual words in a category, we can compile distributions for the entire category, and therefore generate maps for these word categories. For instance, figure FIGREF8 shows the maps created for two categories: Positive Feelings and Money. The maps are not surprising, and interestingly they also reflect an inverse correlation between Money and Positive Feelings .

Human correctness/refusal judgment: pending.

## 29. Does the corpus contain only English documents?

Paper: `1704.04452`; question: `8e44c02c2d9fa56fb74ace35ee70a5add50b52ae`; request: `2e89e053de0747af88b9e684701e2943`.
Saved status: **insufficient_evidence**. Human review: **pending**.

### Supplied passages

`1704.04452:s0014:p0001:c0000` - Document Clusters; source characters 0:454.

> Because we used a large web crawl as the source for our corpus, it contains documents from a variety of genres. To further analyze this property, we categorized a sample of 50 documents from the corpus. Among them, we found professionally written articles and blog posts (28%), educational material for parents and kids (26%), personal blog posts (16%), forum discussions and comments (12%), commented link collections (12%) and scientific articles (6%).

`1704.04452:s0014:p0000:c0000` - Document Clusters; source characters 0:717.

> The corpus consists of document clusters for 30 different topics. Each of them contains around 40 documents with on average 2413 tokens, which leads to an average cluster size of 97,880 token. With these characteristics, the document clusters are 15 times larger than typical DUC clusters of ten documents and five times larger than the 25-document-clusters (Table TABREF26 ). In addition, the documents are also more variable in terms of length, as the (length-adjusted) standard deviation is twice as high as in the other corpora. With these properties, the corpus represents an interesting challenge towards real-world application scenarios, in which users typically have to deal with much more than ten documents.

`1704.04452:s0000:p0004:c0000` - Introduction; source characters 0:606.

> As a crucial step of the corpus creation, we developed a new crowdsourcing scheme called low-context importance annotation. In contrast to traditional approaches, it allows us to determine important elements in a document cluster without requiring annotators to read all documents, making it feasible to crowdsource the task and overcome quality issues observed in previous work BIBREF13 . We show that the approach creates reliable data for our focused summarization scenario and, when tested on traditional summarization corpora, creates annotations that are similar to those obtained by earlier efforts.

`1704.04452:s0006:p0000:c0000` - Corpus Creation; source characters 0:447.

> This section presents the corpus construction process, as outlined in Figure FIGREF16 , combining automatic preprocessing, scalable crowdsourcing and high-quality expert annotations to be able to scale to the size of our document clusters. For every topic, we spent about $150 on crowdsourcing and 1.5h of expert annotations, while just a single annotator would already need over 8 hours (at 200 words per minute) to read all documents of a topic.

`1704.04452:s0015:p0001:c0000` - Concept Maps; source characters 0:572.

> To obtain a better picture of what kind of text spans have been used as labels, we automatically tagged them with their part-of-speech and determined their head with a dependency parser. Concept labels tend to be headed by nouns (82%) or verbs (15%), while they also contain adjectives, prepositions and determiners. Relation labels, on the other hand, are almost always headed by a verb (94%) and contain prepositions, nouns and particles in addition. These distributions are very similar to those reported by Villalon.2010 for their (single-document) concept map corpus.

Human correctness/refusal judgment: pending.

## 30. How are the interpretability merits of the approach demonstrated?

Paper: `1912.00667`; question: `67e9e147b2cab5ba43572ce8a17fc863690172f0`; request: `de7b8cc820bf4035ae4fa8a59446e0dd`.
Saved status: **answered**. Human review: **pending**.

### Claim 1

The approach demonstrates interpretability by directly soliciting informative keywords from the crowd, which serve as human‑understandable explanations for the improved model and make the training process more transparent.

Citations: `1912.00667:abstract:p0000:c0001`, `1912.00667:s0012:p0001:c0001`

Human support: pending. Human note:

### Cited passages

`1912.00667:abstract:p0000:c0001` - Abstract; source characters 883:1312.

> the model in order to discover new keywords that are most beneficial for model training. These keywords and their expectation not only improve the resulting performance but also make the model training process more transparent. We empirically demonstrate the merits of our approach, both in terms of accuracy and interpretability, on multiple real-world datasets and show that our approach improves the state of the art by 24.3%.

`1912.00667:s0012:p0001:c0001` - Related Work; source characters 720:1040.

> BIBREF11, BIBREF35, BIBREF12, for which humans are increasingly involved, for instance for post-hoc evaluations of the model's interpretability. In contrast, our approach directly solicits informative keywords from the crowd for model training, thereby providing human-understandable explanations for the improved model.

Human correctness/refusal judgment: pending.
