# Human claim-support review: 30 validation responses

All labels below are from Codex agent inspection. No response has been human-reviewed.
Review the quoted passages, then fill each Human support/correctness field and check its review box.
Support labels: fully_supported, partially_supported, unsupported. Judge question correctness separately.
A refusal has no claims; judge whether the supplied context justified refusing. Errors stay errors.
Use the rubric in [evaluation.md](../docs/evaluation.md). Original run: validation-qa-baseline-30.

These are validation cases. No held-out test answers are included.

## 1. What data was presented to the subjects to elicit event-related responses?

Question ID: `e6583c60b13b87fc37af75ffc975e7e316d4f4e0`; paper: `1904.04358`.
Status: **answered**. Request: `8aefb3a8347744d8a55b1ea9c71d4df0`.

- [ ] Human reviewed

Human correctness: **pending**

Benchmark references (annotations can disagree):
- 7 phonemic/syllabic ( /iy/, /piy/, /tiy/, /diy/, /uw/, /m/, /n/ ) as well as 4 words(pat, pot, knew and gnaw)
- KARA ONE BIBREF17 , composed of multimodal data for stimulus-based, imagined and articulated speech state corresponding to 7 phonemic/syllabic ( /iy/, /piy/, /tiy/, /diy/, /uw/, /m/, /n/ ) as well as 4 words(pat, pot, knew and gnaw)

Agent response assessment: **partially_correct**. Correct phoneme/word list matches the references; the cited paragraph does not explicitly establish that prompts were auditory.

### Claim 1

The subjects were presented with auditory prompts consisting of seven phonemic/syllabic sounds (/iy/, /piy/, /tiy/, /diy/, /uw/, /m/, /n/) and four whole words (pat, pot, knew, gnaw).

Agent support: **partially_supported**. The list and presentation are supported. The auditory qualifier is not explicit in this cited span.

Human support: **pending**

Human note: 

<details><summary>Cited source passages</summary>

`1904.04358:s0007:p0000:c0000` — Dataset, characters 0:788

> We evaluate our model on a publicly available dataset, KARA ONE BIBREF17 , composed of multimodal data for stimulus-based, imagined and articulated speech state corresponding to 7 phonemic/syllabic ( /iy/, /piy/, /tiy/, /diy/, /uw/, /m/, /n/ ) as well as 4 words(pat, pot, knew and gnaw). The dataset consists of 14 participants, with each prompt presented 11 times to each individual. Since our intention is to classify the phonological categories from human thoughts, we discard the facial and audio information and only consider the EEG data corresponding to imagined speech. It is noteworthy that given the mixed nature of EEG signals, it is reportedly challenging to attain a pairwise EEG-phoneme mapping BIBREF18 . In order to explore the problem space, we thus specifically target 

</details>

## 2. Can named entities in SnapCaptions be discontigious?

Question ID: `a0543b4afda15ea47c1e623c7f00d4aaca045be0`; paper: `1802.07862`.
Status: **insufficient_evidence**. Request: `a46878c9515d4c6d95f21355652b0ac7`.

- [ ] Human reviewed

Human correctness: **pending**

Benchmark references (annotations can disagree):
- No
- Unanswerable

Agent response assessment: **refusal**. Supplied passages describe SnapCaptions and NER but do not specify entity contiguity. Gold annotations disagree (No versus Unanswerable); exclude from consensus abstention denominators.

<details><summary>Supplied passages for refusal/error inspection</summary>

`1802.07862:s0006:p0000:c0001` — SnapCaptions Dataset, characters 756:1344

> available). We split the dataset into train (70%), validation (15%), and test sets (15%). The captions data have average length of 30.7 characters (5.81 words) with vocabulary size 15,733, where 6,612 are considered unknown tokens from Stanford GloVE embeddings BIBREF22 . Named entities annotated in the SnapCaptions dataset include many of new and emerging entities, and they are found in various surface forms (various nicknames, typos, etc.) To the best of our knowledge, SnapCaptions is the only dataset that contains natural image-caption pairs with expert-annotated named entities.

`1802.07862:s0000:p0002:c0000` — Introduction, characters 0:757

> To address the challenges above for social media posts, we build upon the state-of-the-art neural architecture for NER with the following two novel approaches (Figure FIGREF1 ). First, we propose to leverage auxiliary modalities for additional context resolution of entities. For example, many popular social media platforms now provide ways to compose a post in multiple modalities - specifically image and text (e.g. Snapchat captions, Twitter posts with image URLs), from which we can obtain additional context for understanding posts. While â€œmonopoly" in the previous example is ambiguous in its textual form, an accompanying snap image of a board game can help disambiguate among polysemous entities, thereby correctly recognizing it as a named entity.

`1802.07862:abstract:p0000:c0000` — Abstract, characters 0:910

> We introduce a new task called Multimodal Named Entity Recognition (MNER) for noisy user-generated data such as tweets or Snapchat captions, which comprise short text with accompanying images. These social media posts often come in inconsistent or incomplete syntax and lexical notations with very limited surrounding textual contexts, bringing significant challenges for NER. To this end, we create a new dataset for MNER called SnapCaptions (Snapchat image-caption pairs submitted to public and crowd-sourced stories with fully annotated named entities). We then build upon the state-of-the-art Bi-LSTM word/character based NER models with 1) a deep image network which incorporates relevant visual context to augment textual information, and 2) a generic modality-attention module which learns to attenuate irrelevant modalities while amplifying the most informative ones to extract contexts from, adaptive 

`1802.07862:s0006:p0000:c0000` — SnapCaptions Dataset, characters 0:859

> The SnapCaptions dataset is composed of 10K user-generated image (snap) and textual caption pairs where named entities in captions are manually labeled by expert human annotators (entity types: PER, LOC, ORG, MISC). These captions are collected exclusively from snaps submitted to public and crowd-sourced stories (aka Snapchat Live Stories or Our Stories). Examples of such public crowd-sourced stories are â€œNew York Storyâ€‌ or â€œThanksgiving Storyâ€‌, which comprise snaps that are aggregated for various public events, venues, etc. All snaps were posted between year 2016 and 2017, and do not contain raw images or other associated information (only textual captions and obfuscated visual descriptor features extracted from the pre-trained InceptionNet are available). We split the dataset into train (70%), validation (15%), and test sets (15%). The captions 

`1802.07862:s0000:p0001:c0000` — Introduction, characters 0:816

> While many previous approaches BIBREF0 , BIBREF1 , BIBREF2 , BIBREF3 on NER have shown success for well-formed text in recognizing named entities via word context resolution (e.g. LSTM with word embeddings) combined with character-level features (e.g. CharLSTM/CNN), several additional challenges remain for recognizing named entities from extremely short and coarse text found in social media posts. For instance, short social media posts often do not provide enough textual contexts to resolve polysemous entities (e.g. â€œmonopoly is da best ", where `monopoly' may refer to a board game (named entity) or a term in economics). In addition, noisy text includes a huge number of unknown tokens due to inconsistent lexical notations and frequent mentions of various newly trending entities (e.g. â€œxoxo Marshmelloooo "

</details>

## 3. What kind of stylistic features are obtained?

Question ID: `22732cb9476e521452bf0538f3fdb94cf3867651`; paper: `1701.05574`.
Status: **answered**. Request: `4c3de940e2a743d9b01cb6dbed6a6c27`.

- [ ] Human reviewed

Human correctness: **pending**

Benchmark references (annotations can disagree):
- Unanswerable

Agent response assessment: **incorrect**. The answer conflates cognitive gaze features with stylistic features. The supplied abstract explicitly distinguishes them; the gold annotation is unanswerable.

### Claim 1

The paper obtains stylistic features in the form of simple gaze-based features derived from eyeأ¢â‚¬â€کmovement attributes such as fixations, forward saccades, skips and regressions, and complex features derived from a graph structure built over the eyeأ¢â‚¬â€کmovement data.

Agent support: **unsupported**. Cited text supports the gaze feature details, but labels them cognitive, not stylistic. The main category asserted by the answer is unsupported.

Human support: **pending**

Human note: 

<details><summary>Cited source passages</summary>

`1701.05574:s0017:p0000:c0000` — Conclusion, characters 0:710

> In the current work, we created a novel framework to detect sarcasm, that derives insights from human cognition, that manifests over eye movement patterns. We hypothesized that distinctive eye-movement patterns, associated with reading sarcastic text, enables improved detection of sarcasm. We augmented traditional linguistic features with cognitive features obtained from readers' eye-movement data in the form of simple gaze-based features and complex features derived from a graph structure. This extended feature-set improved the success rate of the sarcasm detector by 3.7%, over the best available system. Using cognitive features in an NLP Processing system like ours is the first proposal of its kind.

`1701.05574:s0009:p0000:c0000` — Simple Gaze Based Features, characters 0:876

> Readers' eye-movement behavior, characterized by fixations, forward saccades, skips and regressions, can be directly quantified by simple statistical aggregation (i.e., either computing features for individual participants and then averaging or performing a multi-instance based learning as explained in section SECREF6 ). Since these eye-movement attributes relate to the cognitive process in reading BIBREF17 , we consider these as features in our model. Some of these features have been reported by sarcasmunderstandability for modeling sarcasm understandability of readers. However, as far as we know, these features are being introduced in NLP tasks like textual sarcasm detection for the first time. The values of these features are believed to increase with the increase in the degree of surprisal caused by incongruity in text (except skip count, which will decrease).

</details>

## 4. Does their NER model learn NER from both text and images?

Question ID: `adbf33c6144b2f5c40d0c6a328a92687a476f371`; paper: `1802.07862`.
Status: **answered**. Request: `75ce2e35d73c461d9d98d614827d6bbc`.

- [ ] Human reviewed

Human correctness: **pending**

Benchmark references (annotations can disagree):
- Yes
- Yes

Agent response assessment: **correct**. Both references say Yes; cited architecture and contribution text directly describe joint text/image NER.

### Claim 1

The MNER model learns named entity recognition by jointly using both text and image modalities.

Agent support: **fully_supported**. The two citations explicitly specify image and text inputs and multimodal label prediction.

Human support: **pending**

Human note: 

<details><summary>Cited source passages</summary>

`1802.07862:s0000:p0004:c0000` — Introduction, characters 0:851

> Our contributions are three-fold: we propose (1) an LSTM-CNN hybrid multimodal NER network that takes as input both image and text for recognition of a named entity in text input. To the best of our knowledge, our approach is the first work to incorporate visual contexts for named entity recognition tasks. (2) We propose a general modality attention module that selectively chooses modalities to extract primary context from, maximizing information gain and suppressing irrelevant contexts from each modality (we treat words, characters, and images as separate modalities). (3) We show that the proposed approaches outperform the state-of-the-art NER models (both with and without using additional visual contexts) on our new MNER dataset SnapCaptions, a large collection of informal and extremely short social media posts paired with unique images.

`1802.07862:s0002:p0000:c0000` — Proposed Methods, characters 0:586

> Figure FIGREF2 illustrates the proposed multimodal NER (MNER) model. First, we obtain word embeddings, character embeddings, and visual features (Section SECREF3 ). A Bi-LSTM-CRF model then takes as input a sequence of tokens, each of which comprises a word token, a character sequence, and an image, in their respective representation (Section SECREF4 ). At each decoding step, representations from each modality are combined via the modality attention module to produce an entity label for each token ( SECREF5 ). We formulate each component of the model in the following subsections.

</details>

## 5. What future possible improvements are listed?

Question ID: `d915b401bb96c9f104a0353bef9254672e6f5a47`; paper: `1912.10011`.
Status: **insufficient_evidence**. Request: `cc36f07d4c6844359b8e3d055df09ff7`.

- [ ] Human reviewed

Human correctness: **pending**

Benchmark references (annotations can disagree):
- rther constrain the model on the data structure in order to prevent inaccurate of even contradictory descriptions
- to further constrain the model on the data structure in order to prevent inaccurate of even contradictory descriptions

Agent response assessment: **refusal**. A consensus-answerable question is refused because the supplied context discusses evaluation/setup rather than the future constraint improvement in the references. Retrieval miss; still a false refusal in product metrics.

<details><summary>Supplied passages for refusal/error inspection</summary>

`1912.10011:s0008:p0000:c0000` — Experimental setup ::: Evaluation metrics, characters 0:239

> We evaluate our model through two types of metrics. The BLEU score BIBREF34 aims at measuring to what extent the generated descriptions are literally closed to the ground truth. The second category designed by BIBREF10 is more qualitative.

`1912.10011:s0010:p0004:c0000` — Experimental setup ::: Evaluation metrics ::: Information extraction-oriented metrics., characters 0:453

> CS primarily targets the â€œwhat to say" aspect of evaluation, CO targets the â€œhow to say it" aspect, and RG targets both. Note that for CS, CO, RG-% and BLEU metrics, higher is better; which is not true for RG-#. The IE system used in the experiments is able to extract an average of 17 factual records from gold descriptions. In order to mimic a human expert, a generative system should approach this number and not overload generation with brute facts.

`1912.10011:s0014:p0001:c0000` — Results, characters 0:644

> Our results on the RotoWire testset are summarized in Table TABREF25. For each proposed variant of our architecture, we report the mean score over ten runs, as well as the standard deviation in subscript. Results are compared to baselines BIBREF12, BIBREF13, BIBREF10 and variants of our models. We also report the result of the oracle (metrics on the gold descriptions). Please note that gold descriptions trivially obtain 100% on all metrics expect RG, as they are all based on comparison with themselves. RG scores are different, as the IE system is imperfect and fails to extract accurate entities 4% of the time. RG-# is an absolute count.

`1912.10011:s0011:p0004:c0000` — Experimental setup ::: Baselines, characters 0:307

> $\bullet $ Puduppully-updt BIBREF13. It consists in a standard encoder-decoder, with an added module aimed at updating record representations during the generation process. At each decoding step, a gated recurrent network computes which records should be updated and what should be their new representation.

`1912.10011:s0013:p0000:c0000` — Experimental setup ::: Implementation details, characters 0:754

> The decoder is the one used in BIBREF12, BIBREF13, BIBREF10 with the same hyper-parameters. For the encoder module, both the low-level and high-level encoders use a two-layers multi-head self-attention with two heads. To fit with the small number of record keys in our dataset (39), their embedding size is fixed to 20. The size of the record value embeddings and hidden layers of the Transformer encoders are both set to 300. We use dropout at rate 0.5. The models are trained with a batch size of 64. We follow the training procedure in BIBREF21 and train the model for a fixed number of 25K updates, and average the weights of the last 5 checkpoints (at every 1K updates) to ensure more stability across runs. All models were trained with the Adam opt

</details>

## 6. How many electrodes were used on the subject in EEG sessions?

Question ID: `c7b6e6cb997de1660fd24d31759fe6bb21c7863f`; paper: `1904.04358`.
Status: **insufficient_evidence**. Request: `e6b8e6b9ff6a495cb305cb8b375ba217`.

- [ ] Human reviewed

Human correctness: **pending**

Benchmark references (annotations can disagree):
- 1913 signals
- Unanswerable

Agent response assessment: **refusal**. No electrode count appears in supplied context. One annotation's 1913 is the number of signals, not electrodes; the other says unanswerable. Refusal avoids conflating these counts.

<details><summary>Supplied passages for refusal/error inspection</summary>

`1904.04358:s0000:p0001:c0000` — Introduction, characters 0:942

> Among the various brain activity-monitoring modalities in BCI, electroencephalography (EEG) BIBREF5 , BIBREF6 has demonstrated promising potential to differentiate between various brain activities through measurement of related electric fields. EEG is non-invasive, portable, low cost, and provides satisfactory temporal resolution. This makes EEG suitable to realize BCI systems. EEG data, however, is challenging: these data are high dimensional, have poor SNR, and suffer from low spatial resolution and a multitude of artifacts. For these reasons, it is not particularly obvious how to decode the desired information from raw EEG signals. Although the area of BCI based speech intent recognition has received increasing attention among the research community in the past few years, most research has focused on classification of individual speech categories in terms of discrete vowels, phonemes and words BIBREF7 , BIBREF8 , BIBREF9 , BI

`1904.04358:s0008:p0000:c0000` — Training and hyperparameter selection, characters 0:571

> We performed two sets of experiments with the single-trial EEG data. In PHASE-ONE, our goals was to identify the best architectures and hyperparameters for our networks with a reasonable number of runs. For PHASE-ONE, we randomly shuffled and divided the data (1913 signals from 14 individuals) into train (80%), development (10%) and test sets (10%). In PHASE-TWO, in order to perform a fair comparison with the previous methods reported on the same dataset, we perform a leave-one-subject out cross-validation experiment using the best settings we learn from PHASE-ONE.

`1904.04358:s0003:p0000:c0000` — Joint variability of electrodes, characters 0:959

> Multichannel EEG data is high dimensional multivariate time series data whose dimensionality depends on the number of electrodes. It is a major hurdle to optimally encode information from these EEG data into lower dimensional space. In fact, our investigation based on a development set (as we explain later) showed that well-known deep neural networks (e.g., fully connected networks such as convolutional neural networks, recurrent neural networks and autoencoders) fail to individually learn such complex feature representations from single-trial EEG data. Besides, we found that instead of using the raw multi-channel high-dimensional EEG requiring large training times and resource requirements, it is advantageous to first reduce its dimensionality by capturing the information transfer among the electrodes. Instead of the conventional approach of selecting a handful of channels as BIBREF17 , BIBREF18 , we address this by computing the channel cross-

`1904.04358:s0009:p0003:c0000` — Performance analysis and discussion, characters 0:688

> Next, we provide performance comparison of the proposed approach with the baseline methods for PHASE-TWO of our study (cross-validation experiment) in Table TABREF15 . Since the model encounters the unseen data of a new subject for testing, and given the high inter-subject variability of the EEG data, a reduction in the accuracy was expected. However, our network still managed to achieve an improvement of 18.91, 9.95, 67.15, 2.83 and 13.70 % over BIBREF17 . Besides, our best model shows more reliability compared to previous works: The standard deviation of our model's classification accuracy across all the tasks is reduced from 22.59% BIBREF17 and 17.52% BIBREF18 to a mere 5.41%.

`1904.04358:s0000:p0002:c0000` — Introduction, characters 0:950

> Production of articulatory speech is an extremely complicated process, thereby rendering understanding of the discriminative EEG manifold corresponding to imagined speech highly challenging. As a result, most of the existing approaches failed to achieve satisfactory accuracy on decoding speech tokens from the speech imagery EEG data. Perhaps, for these reasons, very little work has been devoted to relating the brain signals to the underlying articulation. The few exceptions include BIBREF17 , BIBREF18 . In BIBREF17 , Zhao et al. used manually handcrafted features from EEG data, combined with speech audio and facial features to achieve classification of the phonological categories varying based on the articulatory steps. However, the imagined speech classification accuracy based on EEG data alone, as reported in BIBREF17 , BIBREF18 , are not satisfactory in terms of accuracy and reliability. We now turn to describing our proposed models.

</details>

## 7. Did they use a crowdsourcing platform?

Question ID: `49764eee7fb523a6a28375cc699f5e0220b81766`; paper: `1908.05441`.
Status: **insufficient_evidence**. Request: `13bde354e5d944e1bb602bda4cc32f9a`.

- [ ] Human reviewed

Human correctness: **pending**

Benchmark references (annotations can disagree):
- No
- No

Agent response assessment: **refusal**. Both gold references say No. Supplied annotation procedure describes two annotators (one domain expert) resolving disagreements, but does not explicitly name or rule out a platform. Gold false refusal; context-level negative inference remains debatable.

<details><summary>Supplied passages for refusal/error inspection</summary>

`1908.05441:s0011:p0005:c0000` — Annotation, characters 0:527

> Interannotator Agreement: To increase quality and consistency, each annotator annotated the entire dataset of 7,787 questions. Two annotators were used, with the lead annotator possessing previous professional domain expertise. Annotation proceeded in a two-stage process, where in stage 1 annotators completed their annotation independently, and in stage 2 each of the questions where the annotators did not have complete agreement were manually resolved by the annotators, resulting in high-quality classification annotation.

`1908.05441:s0012:p0006:c0000` — Question Classification, characters 0:926

> Topic words: We made use of the 77 TREC word lists of Li and Roth BIBREF6 , containing a total of 3,257 terms, as well as an in-house set of 144 word lists on general and elementary science topics mined from the web, such as ANIMALS, VEGETABLES, and VEHICLES, containing a total of 29,059 words. To mitigate sparsity, features take the form of counts for a specific topic â€“ detecting the words turtle and giraffe in a question would provide a count of 2 for the ANIMAL feature. This provides a light form of domain-specific entity and action (e.g. types of changes) recognition. Pilot experiments showed that this wordlist feature did add a modest performance benefit of approximately 2% to question classification accuracy. Taken together with our results on hypernym expansion, this suggests that manually curated wordlists can show modest benefits for question classification performance, but at the expense of substantial 

`1908.05441:s0011:p0001:c0000` — Annotation, characters 0:867

> Annotation Procedure: Primary annotation took place over approximately 8 weeks. Annotators were instructed to provide up to 2 labels from the full classification taxonomy (462 labels) that were appropriate for each question, and to provide the most specific label available in the taxonomy for a given question. Of the 462 labels in the classification taxonomy, the ARC questions had non-zero counts in 406 question types. Rarely, questions were encountered by annotators that did not clearly fit into a label at the end of the taxonomy, and in these cases the annotators were instructed to choose a more generic label higher up the taxonomy that was appropriate. This occurred when the production taxonomy failed to have specific categories for infrequent questions testing knowledge that is not a standard part of the science curriculum. For example, the question: 

`1908.05441:s0012:p0005:c0000` — Question Classification, characters 0:652

> Similar to query expansion using WordNet Hypernyms, our pilot experiments did not observe a benefit to using Probase hypernyms over the baseline model. An error analysis suggested that the large number of noisy and out-of-context links present in Probase may have reduced performance, and in response we constructed a filtered list of 710 key hypernym categories manually filtered from a list of hypernyms seeded using high-frequency words from an in-house corpus of 250 in-domain science textbooks. We also did not observe a benefit to question classification over the baseline model when expanding only to this manually curated list of key hypernyms.

`1908.05441:s0011:p0004:c0000` — Annotation, characters 0:408

> Questions from the training, development, and test sets were randomly shuffled to counterbalance any learning effects during the annotation procedure, but were presented in grade order (3rd to 9th grade) to reduce context switching (a given grade level tends to use a similar subset of the taxonomy â€“ for example, 3rd grade questions generally do not address Chemical Equations or Newtons 1st Law of Motion).

</details>

## 8. What dataset was used?

Question ID: `df5a4505edccc0ee11349ed6e7958cf6b84c9ed4`; paper: `1910.09982`.
Status: **answered**. Request: `f309260a88954c60880842246be45e95`.

- [ ] Human reviewed

Human correctness: **pending**

Benchmark references (annotations can disagree):
-  news articles in free-text format
- collected from 36 propagandist and 12 non-propagandist news outlets and then annotated by professional annotators

Agent response assessment: **partially_correct**. The annotation company is correctly identified, but the response omits the news-article source and outlet composition that identify the dataset in the references.

### Claim 1

The dataset used for the shared task was a corpus annotated by A Data Pro.

Agent support: **fully_supported**. The cited paragraph explicitly says the task corpus was annotated by A Data Pro.

Human support: **pending**

Human note: 

<details><summary>Cited source passages</summary>

`1910.09982:s0035:p0001:c0000` — Acknowledgments, characters 0:109

> The corpus for the task was annotated by A Data Pro, a company that performs high-quality manual annotations.

</details>

## 9. Which real-world datasets are used?

Question ID: `3941401a182a3d6234894a5c8a75d48c6116c45c`; paper: `1912.00667`.
Status: **answered**. Request: `0d37b6185d49497992260a826f2b272f`.

- [ ] Human reviewed

Human correctness: **pending**

Benchmark references (annotations can disagree):
- Tweets related to CyberAttack and tweets related to PoliticianDeath
- cyber security (CyberAttack), death of politicians (PoliticianDeath)

Agent response assessment: **correct**. Both dataset names and Twitter collection source match the references and the cited dataset paragraph.

### Claim 1

The study uses two realأ¢â‚¬â€کworld datasets: a CyberAttack dataset and a PoliticianDeath dataset, both collected from Twitter.

Agent support: **fully_supported**. Both event categories and their collection from Twitter are explicitly described in the two cited windows.

Human support: **pending**

Human note: 

<details><summary>Cited source passages</summary>

`1912.00667:s0007:p0000:c0000` — Experiments and Results ::: Experimental Setup, characters 0:907

> Datasets. We perform our experiments with two predetermined event categories: cyber security (CyberAttack) and death of politicians (PoliticianDeath). These event categories are chosen as they are representative of important event types that are of interest to many governments and companies. The need to create our own dataset was motivated by the lack of public datasets for event detection on microposts. The few available datasets do not suit our requirements. For example, the publicly available Events-2012 Twitter dataset BIBREF20 contains generic event descriptions such as Politics, Sports, Culture etc. Our work targets more specific event categories BIBREF21. Following previous studies BIBREF1, we collect event-related microposts from Twitter using 11 and 8 seed events (see Section SECREF2) for CyberAttack and PoliticianDeath, respectively. Unlabeled microposts are collected by using the key

`1912.00667:s0007:p0000:c0001` — Experiments and Results ::: Experimental Setup, characters 783:1232

> (see Section SECREF2) for CyberAttack and PoliticianDeath, respectively. Unlabeled microposts are collected by using the keyword `hack' for CyberAttack, while for PoliticianDeath, we use a set of keywords related to `politician' and `death' (such as `bureaucrat', `dead' etc.) For each dataset, we randomly select 500 tweets from the unlabeled subset and manually label them for evaluation. Table TABREF25 shows key statistics from our two datasets.

</details>

## 10. Which qualitative metric are used for evaluation?

Question ID: `79a44a68bb57b375d8a57a0a7f522d33476d9f33`; paper: `1912.10011`.
Status: **answered**. Request: `8d0fee589e114eedb7abc756f8223a70`.

- [ ] Human reviewed

Human correctness: **pending**

Benchmark references (annotations can disagree):
-  Relation Generation (RG) , Content Selection (CS),  Content Ordering (CO)
- Relation Generation (RG), Content Selection (CS), Content Ordering (CO)

Agent response assessment: **partially_correct**. Identifies CS, CO, and RG, but incorrectly expands RG as referential generation instead of relation generation. The cited paragraph does not supply the expansions.

### Claim 1

The qualitative evaluation metrics used are CS (content selection), CO (content ordering), RG (referential generation), RG-% (referential generation percentage), and RG-# (referential generation count).

Agent support: **partially_supported**. The metric abbreviations and RG variants appear in the cited span. The invented expansion of RG is wrong; expansion claims are not established by this citation.

Human support: **pending**

Human note: 

<details><summary>Cited source passages</summary>

`1912.10011:s0010:p0004:c0000` — Experimental setup ::: Evaluation metrics ::: Information extraction-oriented metrics., characters 0:453

> CS primarily targets the â€œwhat to say" aspect of evaluation, CO targets the â€œhow to say it" aspect, and RG targets both. Note that for CS, CO, RG-% and BLEU metrics, higher is better; which is not true for RG-#. The IE system used in the experiments is able to extract an average of 17 factual records from gold descriptions. In order to mimic a human expert, a generative system should approach this number and not overload generation with brute facts.

</details>

## 11. what previous RNN models do they compare with?

Question ID: `6aaf12505add25dd133c7b0dafe8f4fe966d1f1d`; paper: `1808.09029`.
Status: **insufficient_evidence**. Request: `305bfac21e96463bb3aaf3eb02b9b451`.

- [ ] Human reviewed

Human correctness: **pending**

Benchmark references (annotations can disagree):
- Variational LSTM, CharCNN, Pointer Sentinel-LSTM, RHN, NAS Cell, SRU, QRNN, RAN, 4-layer skip-connection LSTM, AWD-LSTM, Quantized LSTM

Agent response assessment: **refusal**. The supplied introduction/PRU paragraphs do not contain the requested comparison-model list. The selected-set benchmark still retains this refused answerable case.

<details><summary>Supplied passages for refusal/error inspection</summary>

`1808.09029:abstract:p0000:c0001` — Abstract, characters 833:1129

> number of model parameters, PRU outperforms all previous RNN models that exploit different gating mechanisms and transformations. We provide a detailed examination of the PRU and its behavior on the language modeling tasks. Our code is open-source and available at https://sacmehta.github.io/PRU/

`1808.09029:abstract:p0000:c0000` — Abstract, characters 0:1006

> LSTMs are powerful tools for modeling contextual information, as evidenced by their success at the task of language modeling. However, modeling contexts in very high dimensional space can lead to poor generalizability. We introduce the Pyramidal Recurrent Unit (PRU), which enables learning representations in high dimensional space with more generalization power and fewer parameters. PRUs replace the linear transformation in LSTMs with more sophisticated interactions including pyramidal and grouped linear transformations. This architecture gives strong results on word-level language modeling while reducing the number of parameters significantly. In particular, PRU improves the perplexity of a recent state-of-the-art language model Merity et al. (2018) by up to 1.3 points while learning 15-20% fewer parameters. For similar number of model parameters, PRU outperforms all previous RNN models that exploit different gating mechanisms and transformations. We provide a detailed examination of the PR

`1808.09029:s0008:p0004:c0000` — Results, characters 0:532

> PRU is a drop-in replacement for LSTM, therefore, it can improve language models with modern inference techniques such as dynamic evaluation BIBREF21 . When we evaluate PRU-based language models (only with standard dropout) with dynamic evaluation on the PTB test set, the perplexity of PRU ( INLINEFORM0 ) improves from 62.42 to 55.23 while the perplexity of an LSTM ( INLINEFORM1 ) with similar settings improves from 66.29 to 58.79; suggesting that modern inference techniques are equally applicable to PRU-based language models.

`1808.09029:s0002:p0000:c0000` — Pyramidal Recurrent Units, characters 0:386

> We introduce Pyramidal Recurrent Units (PRUs), a new RNN architecture which improves modeling of context by allowing for higher dimensional vector representations while learning fewer parameters. Figure FIGREF2 provides an overview of PRU. We first elaborate on the details of the pyramidal transformation and the grouped linear transformation. We then describe our recurrent unit, PRU.

`1808.09029:s0004:p0000:c0000` — Grouped linear transformation for context, characters 0:525

> Many RNN architectures apply linear transformations to both the input and context vector. However, this may not be ideal due to the differing semantics of each vector. In many NLP applications including language modeling, the input vector is a dense word embedding which is shared across all contexts for a given word in a dataset. In contrast, the context vector is highly contextualized by the current sequence. The differences between the input and context vector motivate their separate treatment in the PRU architecture.

</details>

## 12. What was their system's performance?

Question ID: `bdf93053b1b9b0a21f77ed370cf4d5a10df70e3e`; paper: `1706.01875`.
Status: **answered**. Request: `9d90e5dcd33a478d965f83a72e7493f8`.

- [ ] Human reviewed

Human correctness: **pending**

Benchmark references (annotations can disagree):
- accuracy and F1-score of 89.6% and 89.2%, respectively
- accuracy and F1-score of 89.6% and 89.2%, respectively

Agent response assessment: **correct**. Accuracy, F1, and holdout-set qualifier match the references and the cited performance paragraph.

### Claim 1

The classifier achieved an accuracy of 89.6% and an F1أ¢â‚¬â€کscore of 89.2% on the holdout set.

Agent support: **fully_supported**. The cited span explicitly reports accuracy 89.6% and F1 89.2% on the holdout set.

Human support: **pending**

Human note: 

<details><summary>Cited source passages</summary>

`1706.01875:s0004:p0002:c0000` — Classifier evaluation, characters 0:445

> Real-world classifier performance. To evaluate real-world performance of our selected classifier (i.e., performance in the absence of model and parameter bias), we perform classification of the holdout set. On this set, our classifier had an accuracy and F1-score of 89.6% and 89.2%, respectively. These results show that in addition to superior accuracy during training and validation, our chosen classifier is also robust against over-fitting.

</details>

## 13. Does the experiments focus on a specific domain?

Question ID: `4e1a67f8dc68b55a5ce18e6cd385ae9ab90d891f`; paper: `1703.04001`.
Status: **answered**. Request: `d0276ec0d20947f2abdcdd141321cf49`.

- [ ] Human reviewed

Human correctness: **pending**

Benchmark references (annotations can disagree):
- No
- No

Agent response assessment: **correct**. The references say No; cited crawling procedure deliberately spans genres and 80,253 topics, supporting the broad-domain answer.

### Claim 1

The experiments do not focus on a specific domain; the dataset covers a wide range of topics.

Agent support: **fully_supported**. The wide range of topics and deliberate collection across genres support the conclusion that this is not a single-domain experiment.

Human support: **pending**

Human note: 

<details><summary>Cited source passages</summary>

`1703.04001:s0001:p0000:c0000` — Dataset description, characters 0:771

> We obtained our Quora dataset BIBREF7 through web-based crawls between June 2014 to August 2014. This crawling exercise has resulted in the accumulation of a massive Q&A dataset spanning over a period of over four years starting from January 2010 to May 2014. We initiated crawling with 100 questions randomly selected from different topics so that different genre of questions can be covered. The crawling of the questions follow a BFS pattern through the related question links. We obtained 822,040 unique questions across 80,253 different topics with a total of 1,833,125 answers to these questions. For each question, we separately crawl their revision logs that contain different types of edit information for the question and the activity log of the question asker.

</details>

## 14. What did the best systems use for their model?

Question ID: `b7c3f3942a07c118e57130bc4c3ec4adc431d725`; paper: `1907.03187`.
Status: **answered**. Request: `644f668be1d7408b8cae4e7856b4c136`.

- [ ] Human reviewed

Human correctness: **pending**

Benchmark references (annotations can disagree):
- Unanswerable

Agent response assessment: **incorrect**. The source describes the authors' QRNN choice for speed after similar training performance. It does not establish what plural best systems used; the gold annotation is unanswerable.

### Claim 1

The best systems used a QRNN-based architecture for their language model.

Agent support: **partially_supported**. QRNN use is explicit, but the ranking/attribution to best systems is not established by the cited paragraph.

Human support: **pending**

Human note: 

<details><summary>Cited source passages</summary>

`1907.03187:s0006:p0000:c0001` — LM Training and Fine-tuning, characters 611:905

> We performed some simple tests with LSTM units and a Transformer Language model, finding all models were similar in performance during LM training. We thus chose to use QRNN units due to improved training speed compared to the alternatives. This model has about 60 million trainable parameters.

</details>

## 15. What is NER?

Question ID: `cf874cd9023d901e10aa8664b813d32501e7e4d2`; paper: `1705.05437`.
Status: **answered**. Request: `4f90770b183648098575daa0cedbc679`.

- [ ] Human reviewed

Human correctness: **pending**

Benchmark references (annotations can disagree):
- Named Entity Recognition
- Named Entity Recognition, including entities such as proteins, genes, diseases, treatments, drugs, etc. in the biomedical domain

Agent response assessment: **correct**. The expansion and biomedical examples match the reference and cited definition.

### Claim 1

Named Entity Recognition (NER) in the Biomedical domain usually includes recognition of entities such as proteins, genes, diseases, treatments, drugs, etc.

Agent support: **fully_supported**. The claim reproduces the source's explicit definition and examples.

Human support: **pending**

Human note: 

<details><summary>Cited source passages</summary>

`1705.05437:s0001:p0000:c0000` — Named Entity Recognition and Fact Extraction, characters 0:368

> Named Entity Recognition (NER) in the Biomedical domain usually includes recognition of entities such as proteins, genes, diseases, treatments, drugs, etc. Fact extraction involves extraction of Named Entities from a corpus, usually given a certain ontology. When compared to NER in the domain of general text, the biomedical domain has some characteristic challenges:

</details>

## 16. Do they inspect their model to see if their model learned to associate image parts with words related to entities?

Question ID: `7cd22ca9e107d2b13a7cc94252aaa9007976b338`; paper: `1802.07862`.
Status: **insufficient_evidence**. Request: `4a9d085313b747de9949a093d379de5f`.

- [ ] Human reviewed

Human correctness: **pending**

Benchmark references (annotations can disagree):
- Yes
- Yes

Agent response assessment: **refusal**. Relevant error analysis and modality-attention inspection are supplied, with image-derived contexts associated with entity words. Both gold references say Yes. A qualified answer distinguishing visual tags from spatial image regions would be more useful than a blanket refusal.

<details><summary>Supplied passages for refusal/error inspection</summary>

`1802.07862:s0008:p0003:c0000` — Results: SnapCaptions Dataset, characters 0:877

> Error Analysis: Table TABREF17 shows example cases where incorporation of visual contexts affects prediction of named entities. For example, the token `curry' in the caption â€œThe curry's " is polysemous and may refer to either a type of food or a famous basketball player `Stephen Curry', and the surrounding textual contexts do not provide enough information to disambiguate it. On the other hand, visual contexts (visual tags: `parade', `urban area', ...) provide similarities to the token's distributional semantics from other training examples (snaps from â€œNBA Championship Parade Story"), and thus the model successfully predicts the token as a named entity. Similarly, while the text-only model erroneously predicts `Apple' in the caption â€œGrandma w dat lit Apple Crisp" as an organization (Apple Inc.), the visual contexts (describing objects related to food) help disam

`1802.07862:s0008:p0005:c0000` — Results: SnapCaptions Dataset, characters 0:948

> For the image-aided model (W+C+V; upper row in Figure FIGREF19 ), we confirm that the modality attention successfully attenuates irrelevant signals (selfies, etc.) and amplifies relevant modality-based contexts in prediction of a given token. In the example of â€œdisney word essential = coffee" with visual tags selfie, phone, person, the modality attention successfully attenuates distracting visual signals and focuses on textual modalities, consequently making correct predictions. The named entities in the examples of â€œBeautiful night atop The Space Needle" and â€œSplash Mountain" are challenging to predict because they are composed of common nouns (space, needle, splash, mountain), and thus they often need additional contexts to correctly predict. In the training data, visual contexts make stronger indicators for these named entities (space needle, splash mountain), and the modality attention module successfully attends more to stronger 

`1802.07862:s0002:p0000:c0000` — Proposed Methods, characters 0:586

> Figure FIGREF2 illustrates the proposed multimodal NER (MNER) model. First, we obtain word embeddings, character embeddings, and visual features (Section SECREF3 ). A Bi-LSTM-CRF model then takes as input a sequence of tokens, each of which comprises a word token, a character sequence, and an image, in their respective representation (Section SECREF4 ). At each decoding step, representations from each modality are combined via the modality attention module to produce an entity label for each token ( SECREF5 ). We formulate each component of the model in the following subsections.

`1802.07862:s0008:p0003:c0001` — Results: SnapCaptions Dataset, characters 737:1358

> caption â€œGrandma w dat lit Apple Crisp" as an organization (Apple Inc.), the visual contexts (describing objects related to food) help disambiguate the token, making the model predict it correctly as a non-named entity (a fruit). Trending entities (musicians or DJs such as `CID', `Duke Dumont', `Marshmello', etc.) are also recognized correctly with strengthened contexts from visual information (describing concert scenes) despite lack of surrounding textual contexts. A few cases where visual contexts harmed the performance mostly include visual tags that are unrelated to a token or its surrounding textual contexts.

`1802.07862:s0000:p0003:c0001` — Introduction, characters 683:1307

> NLP tasks combine word and character-level information with naive concatenation, which is vulnerable to noisy social media posts. When an auxiliary image is available, the modality attention module determines to amplify this visual context in disambiguating polysemous entities, or to attenuate visual contexts when they are irrelevant to target named entities, selfies, etc. Note that the proposed modality attention module is distinct from how attention is used in other sequence-to-sequence literature (e.g. attending to a specific token within an input sequence). Section SECREF2 provides the detailed literature review.

</details>

## 17. Why are current ELS's not sufficiently effective?

Question ID: `ef7212075e80bf35b7889dc8dd52fcbae0d1400a`; paper: `1806.05504`.
Status: **answered**. Request: `cb99da59f8554999ba445bae732d1b16`.

- [ ] Human reviewed

Human correctness: **pending**

Benchmark references (annotations can disagree):
- Linked entities may be ambiguous or too common
- linked entities extracted from ELS's have issues because of low precision rates BIBREF11 and design challenges in training datasets BIBREF12 . These issues can be summarized into two parts: ambiguity and coarseness., the linked entities may also be too common to be considered an entity.

Agent response assessment: **correct**. Main causes match reference ambiguity/coarseness and low precision. Some explanatory additions exceed each claim's particular citation despite support elsewhere in the response.

### Claim 1

Current entity linking systems (ELS) suffer from low precision, leading to many incorrectly linked entities that degrade downstream tasks.

Agent support: **partially_supported**. Low precision is explicit. Downstream degradation is established in the other cited paragraph, not this claim's cited span.

Human support: **pending**

Human note: 

### Claim 2

The extracted entities often exhibit ambiguity and coarseness, meaning that the same entity can refer to multiple concepts or be too general to be useful.

Agent support: **partially_supported**. Ambiguity/coarseness are named in the citation, but the expanded definitions are not stated in that span.

Human support: **pending**

Human note: 

### Claim 3

These issues result in irrelevant or noisy entity representations that are not helpful for summarization, as soft attention may assign nonأ¢â‚¬â€کnegligible importance to erroneous entities.

Agent support: **fully_supported**. The cited paragraph directly describes erroneous/irrelevant entities receiving non-negligible soft-attention scores and adding noise.

Human support: **pending**

Human note: 

<details><summary>Cited source passages</summary>

`1806.05504:s0003:p0000:c0000` — Possible issues, characters 0:239

> Despite its usefulness, linked entities extracted from ELS's have issues because of low precision rates BIBREF11 and design challenges in training datasets BIBREF12 . These issues can be summarized into two parts: ambiguity and coarseness.

`1806.05504:s0007:p0000:c0000` — Pooling submodule, characters 0:863

> The entity vectors $\tilde{E}$ are pooled to create a single topic vector $t$ that represents the topic of the summary. One possible pooling technique is to use soft attention BIBREF18 on the vectors to determine the importance value of each vector, which can be done by matching each entity vector with the text vector $s$ from the text encoder as the context vector. The entity vectors are then pooled using weighted sum. One problem with soft attention is that it considers all entity vectors when constructing the topic vector. However, not all entities are important and necessary when generating summaries. Moreover, a number of these entities may be erroneous and irrelevant, as reported in Section "Related work" . Soft attention gives non-negligible important scores to these entities, thus adds unnecessary noise to the construction of the topic vector.

</details>

## 18. What news article sources are used?

Question ID: `61a9ea36ddc37c60d1a51dabcfff9445a2225725`; paper: `1703.10344`.
Status: **insufficient_evidence**. Request: `4ace8384cb844a3c99a3cb448eddca9d`.

- [ ] Human reviewed

Human correctness: **pending**

Benchmark references (annotations can disagree):
- Unanswerable
-  the news external references in Wikipedia

Agent response assessment: **refusal**. A supplied News Articles paragraph explicitly says news references are extracted from Wikipedia entity pages, matching one reference. No individual outlet names are supplied; an answer could state that limitation instead of refusing entirely. Annotations are mixed.

<details><summary>Supplied passages for refusal/error inspection</summary>

`1703.10344:s0000:p0002:c0000` — Introduction, characters 0:651

> To remedy these problems, it is important to identify information sources that contain novel and salient facts to a given entity page. However, not all information sources are equal. The online presence of major news outlets is an authoritative source due to active editorial control and their articles are also a timely container of facts. In addition, their use is in line with current Wikipedia editing practice, as is shown in BIBREF7 that almost 20% of current citations in all entity pages are news articles. We therefore propose news suggestion as a novel task that enhances entity pages and reduces delay while keeping its pages authoritative.

`1703.10344:s0005:p0008:c0000` — Articleâ€“Entity Placement, characters 0:901

> Relative Authority. In this case, we consider the comparative relevance of the news article to the different entities occurring in it. As an example, let us consider the meeting of the Sudanese bishop Elias Taban with Hillary Clinton. Both entities are salient for the meeting. However, in Taban's Wikipedia page, this meeting is discussed prominently with a corresponding news reference, whereas in Hillary Clinton's Wikipedia page it is not reported at all. We believe this is not just an omission in Clinton's page but mirrors the fact that for the lesser known Taban the meeting is big news whereas for the more famous Clinton these kind of meetings are a regular occurrence, not all of which can be reported in what is supposed to be a selection of the most important events for her. Therefore, if two entities co-occur, the news is more relevant for the entity with the lower a priori authority.

`1703.10344:s0008:p0002:c0000` — Datasets, characters 0:449

> News Articles. We extract all news references from the collected Wikipedia entity pages. The extracted news references are associated with the sections in which they appear. In total there were INLINEFORM0 news references, and after crawling we end up with INLINEFORM1 successfully crawled news articles. The details of the news article distribution, and the number of entities and sections from which they are referred are shown in Table TABREF44 .

`1703.10344:abstract:p0000:c0000` — Abstract, characters 0:1067

> Wikipedia entity pages are a valuable source of information for direct consumption and for knowledge-base construction, update and maintenance. Facts in these entity pages are typically supported by references. Recent studies show that as much as 20\% of the references are from online news sources. However, many entity pages are incomplete even if relevant information is already available in existing news articles. Even for the already present references, there is often a delay between the news article publication time and the reference time. In this work, we therefore look at Wikipedia through the lens of news and propose a novel news-article suggestion task to improve news coverage in Wikipedia, and reduce the lag of newsworthy references. Our work finds direct application, as a precursor, to Wikipedia page generation and knowledge-base acceleration tasks that rely on relevant and high quality input sources. We propose a two-stage supervised approach for suggesting news articles to entity pages for a given state of Wikipedia. First, we suggest news 

`1703.10344:s0005:p0012:c0000` — Articleâ€“Entity Placement, characters 0:507

> News Domain Authority. The news domain authority addresses two main aspects. Firstly, if bundled together with the relative authority feature, we can ensure that dependent on the entity authority, we suggest news from authoritative sources, hence ensuring the quality of suggested articles. The second aspect is in a news streaming scenario where multiple news domains report the same event â€” ideally only articles coming from authoritative sources would fulfill the conditions for the news suggestion task.

</details>

## 19. What baseline model is used?

Question ID: `2ee715c7c6289669f11a79743a6b2b696073805d`; paper: `1703.10344`.
Status: **answered**. Request: `495dd830f5dc4719b2936abdee721ed9`.

- [ ] Human reviewed

Human correctness: **pending**

Benchmark references (annotations can disagree):
- For Article-Entity placement, they consider two baselines: the first one using only salience-based features, and the second baseline checks if the entity appears in the title of the article. 

For Article-Section Placement, they consider two baselines: the first picks the section with the highest lexical similarity to the article, and the second one picks the most frequent section.
- B1. The first baseline uses only the salience-based features by Dunietz and Gillick BIBREF11 ., B2. The second baseline assigns the value relevant to a pair INLINEFORM0 , if and only if INLINEFORM1 appears in the title of INLINEFORM2 .

, S1: Pick the section from template INLINEFORM0 with the highest lexical similarity to INLINEFORM1 : S1 INLINEFORM2, S2: Place the news into the most frequent section in INLINEFORM0

Agent response assessment: **partially_correct**. Correctly names one baseline, but omits the title-based article/entity baseline and both section-placement baselines in the references.

### Claim 1

The baseline model used is the salience-based model by Dunietz and Gillick.

Agent support: **fully_supported**. The quoted B1 paragraph directly identifies the salience-based baseline and its authors.

Human support: **pending**

Human note: 

<details><summary>Cited source passages</summary>

`1703.10344:s0005:p0020:c0000` — Articleâ€“Entity Placement, characters 0:94

> B1. The first baseline uses only the salience-based features by Dunietz and Gillick BIBREF11 .

</details>

## 20. How were crowd workers instructed to identify important elements in large document collections?

Question ID: `e9cfbfdf30e48cffdeca58d4ac6fdd66a8b27d7a`; paper: `1704.04452`.
Status: **answered**. Request: `af12f1400f324a7c8fe34033a55e62a8`.

- [ ] Human reviewed

Human correctness: **pending**

Benchmark references (annotations can disagree):
- provide only a description of the document cluster's topic along with the propositions
- They break down the task of importance annotation to the level of single propositions and obtain a score for each proposition indicating its importance in a document cluster, such that a ranking according to the score would reveal what is most important and should be included in a summary.

Agent response assessment: **correct**. Explains proposition-level importance annotation without whole documents and adds the explicit five-point rating procedure. Topic-description detail is omitted, but the central annotation method is correct.

### Claim 1

Crowd workers were instructed to identify important elements by evaluating single propositions extracted from documents, without seeing the full documents, and rating each propositionأ¢â‚¬â„¢s importance on a 5أ¢â‚¬â€کpoint Likert scale.

Agent support: **fully_supported**. The first citation establishes proposition-level tasks and hidden documents; the second explicitly establishes the five-point Likert scale.

Human support: **pending**

Human note: 

<details><summary>Cited source passages</summary>

`1704.04452:s0004:p0000:c0000` — Task Design, characters 0:588

> We break down the task of importance annotation to the level of single propositions. The goal of our crowdsourcing scheme is to obtain a score for each proposition indicating its importance in a document cluster, such that a ranking according to the score would reveal what is most important and should be included in a summary. In contrast to other work, we do not show the documents to the workers at all, but provide only a description of the document cluster's topic along with the propositions. This ensures that tasks are small, simple and can be done quickly (see Figure FIGREF4 ).

`1704.04452:s0004:p0003:c0000` — Task Design, characters 0:524

> Instead of enforcing binary importance decisions, we use a 5-point Likert-scale to allow more fine-grained annotations. The obtained labels are translated into scores (5..1) and the average of all scores for a proposition is used as an estimate for its importance. This follows the idea that while single workers might find the task subjective, the consensus of multiple workers, represented in the average score, tends to be less subjective due to the â€œwisdom of the crowdâ€‌. We randomly group five propositions into a task.

</details>

## 21. What is the baseline?

Question ID: `99e78c390932594bd833be0f5c890af5c605d808`; paper: `1912.04961`.
Status: **answered**. Request: `f115ced00560486483b74bba886d7cea`.

- [ ] Human reviewed

Human correctness: **pending**

Benchmark references (annotations can disagree):
- QA PGNet, Multi-decoder QA PGNet with lookup table embedding
- QA PGNet and Multi-decoder QA PGNet

Agent response assessment: **correct**. Main baseline names match both references. Additional naive baselines are source-supported, although the longer answer lowers lexical F1 against the short reference.

### Claim 1

The baseline models used in the study are QA PGNet and Multi-decoder QA PGNet with lookup table embedding.

Agent support: **fully_supported**. The cited paragraph explicitly names both learning-based baselines and lookup embeddings.

Human support: **pending**

Human note: 

### Claim 2

For the Dosage extraction task, a naive baseline called أ¢â‚¬ع©Nearest Numberأ¢â‚¬â„¢ is used, which predicts the number closest to the Medication Name or أ¢â‚¬ع©noneأ¢â‚¬â„¢ if no number is mentioned or the Medication Name is not detected.

Agent support: **fully_supported**. Nearest Number behavior and its none fallback are explicitly described in the cited paragraph.

Human support: **pending**

Human note: 

### Claim 3

For the Frequency extraction task, a naive baseline called أ¢â‚¬ع©Random Top-3أ¢â‚¬â„¢ is used, which predicts a random Frequency tag from the topأ¢â‚¬â€ک3 most frequent tags in the dataset أ¢â‚¬â€œ {أ¢â‚¬ع©noneأ¢â‚¬â„¢, أ¢â‚¬ع©dailyأ¢â‚¬â„¢, أ¢â‚¬ع©twice a dayأ¢â‚¬â„¢}.

Agent support: **fully_supported**. Random Top-3 and all three frequency tags are explicitly described in the cited paragraph.

Human support: **pending**

Human note: 

<details><summary>Cited source passages</summary>

`1912.04961:s0009:p0000:c0000` — Experiments ::: Model variations, characters 0:162

> We consider QA PGNet and Multi-decoder QA PGNet with lookup table embedding as baseline models and improve on the baselines with other variations described below.

`1912.04961:s0009:p0001:c0000` — Experiments ::: Model variations, characters 0:558

> Apart from learning-based baselines, we also create two naive baselines, one each for the Dosage and Frequency extraction tasks. For Dosage extraction, the baseline we consider is `Nearest Number', where we take the number nearest to the Medication Name as the prediction, and `none' if no number is mentioned or if the Medication Name is not detected in the input. For Frequency extraction, the baseline we consider is `Random Top-3' where we predict a random Frequency tag, from top-3 most frequent ones from our dataset - {`none', `daily', `twice a day'}.

</details>

## 22. How do they demonstrate that this type of EEG has discriminative information about the intended articulatory movements responsible for speech?

Question ID: `7ae38f51243cb80b16a1df14872b72a1f8a2048f`; paper: `1904.04358`.
Status: **answered**. Request: `03596bbf66a24758ba703636ebecb31b`.

- [ ] Human reviewed

Human correctness: **pending**

Benchmark references (annotations can disagree):
- we plot T-distributed Stochastic Neighbor Embedding (tSNE) corresponding to INLINEFORM0 and V/C classification tasks in Fig. FIGREF8 .

Agent response assessment: **partially_correct**. Gives valid classification evidence, but does not explain the t-SNE visualization used in the annotated demonstration. This is a source-supported alternative, not an invented result.

### Claim 1

The authors show that speechأ¢â‚¬â€کimagery EEG contains significant discriminative information about the intended articulatory movements by achieving an average classification accuracy of 77.9% across five binary tasks, which is a 22.5% improvement over prior methods.

Agent support: **fully_supported**. The cited abstract window reports the accuracy, five binary tasks, improvement, and discriminative-information conclusion.

Human support: **pending**

Human note: 

<details><summary>Cited source passages</summary>

`1904.04358:abstract:p0000:c0001` — Abstract, characters 816:1343

> a deep autoencoder. We train the individual networks hierarchically, feeding their combined outputs in a final gradient boosting classification step. Our best models achieve an average accuracy of 77.9% across five different binary classification tasks, providing a significant 22.5% improvement over previous methods. As we also show visually, our work demonstrates that the speech imagery EEG possesses significant discriminative information about the intended articulatory movements responsible for natural speech synthesis.

</details>

## 23. How large is their MNER SnapCaptions dataset?

Question ID: `1591068b747c94f45b948e12edafe74b5e721047`; paper: `1802.07862`.
Status: **answered**. Request: `fcdd08922da24a37af26b901bffd4394`.

- [ ] Human reviewed

Human correctness: **pending**

Benchmark references (annotations can disagree):
- 10K user-generated image (snap) and textual caption pairs
- 10000

Agent response assessment: **correct**. The reported 10,000 image-caption pairs exactly matches both references and the source's 10K count.

### Claim 1

The SnapCaptions dataset contains 10,000 imageأ¢â‚¬â€œcaption pairs.

Agent support: **fully_supported**. The cited dataset paragraph explicitly states 10K image/caption pairs.

Human support: **pending**

Human note: 

<details><summary>Cited source passages</summary>

`1802.07862:s0006:p0000:c0000` — SnapCaptions Dataset, characters 0:859

> The SnapCaptions dataset is composed of 10K user-generated image (snap) and textual caption pairs where named entities in captions are manually labeled by expert human annotators (entity types: PER, LOC, ORG, MISC). These captions are collected exclusively from snaps submitted to public and crowd-sourced stories (aka Snapchat Live Stories or Our Stories). Examples of such public crowd-sourced stories are â€œNew York Storyâ€‌ or â€œThanksgiving Storyâ€‌, which comprise snaps that are aggregated for various public events, venues, etc. All snaps were posted between year 2016 and 2017, and do not contain raw images or other associated information (only textual captions and obfuscated visual descriptor features extracted from the pre-trained InceptionNet are available). We split the dataset into train (70%), validation (15%), and test sets (15%). The captions 

</details>

## 24. How did they extend LAMA evaluation framework to focus on negation?

Question ID: `78292bc57ee68fdb93ed45430d80acca25a9e916`; paper: `1911.03343`.
Status: **answered**. Request: `c7570178fdb94246af574a49ae8d0866`.

- [ ] Human reviewed

Human correctness: **pending**

Benchmark references (annotations can disagree):
- To this end, we introduce the negated LAMA dataset. We construct it by simply inserting negation elements (e.g., â€œnotâ€‌) in LAMA cloze statement
- Create the negated LAMA dataset and  query the pretrained language models with both original LAMA and negated LAMA statements and compare their predictions.

Agent response assessment: **partially_correct**. Restates that a negation component was added but does not explain construction by inserting negation elements or comparing original versus negated prompts, as the references do.

### Claim 1

They extended the LAMA evaluation framework by adding a component that focuses on negation.

Agent support: **fully_supported**. The abstract explicitly states an extension of LAMA with a component focused on negation; the response remains too vague about how it works.

Human support: **pending**

Human note: 

<details><summary>Cited source passages</summary>

`1911.03343:abstract:p0000:c0000` — Abstract, characters 0:557

> Pretrained language models have achieved remarkable improvements in a broad range of natural language processing tasks, including question answering (QA). To analyze pretrained language model performance on QA, we extend the LAMA (Petroni et al., 2019) evaluation framework by a component that is focused on negation. We find that pretrained language models are equally prone to generate facts ("birds can fly") and their negation ("birds cannot fly"). This casts doubt on the claim that pretrained language models have adequately learned factual knowledge.

</details>

## 25. what data did they use?

Question ID: `7bd6a6ec230e1efb27d691762cc0674237dc7967`; paper: `1808.09029`.
Status: **answered**. Request: `d5045ab6d8004899940cea8af6366db3`.

- [ ] Human reviewed

Human correctness: **pending**

Benchmark references (annotations can disagree):
-  Penn Treebank, WikiText2
- Penn Treebank (PTB) , WikiText2 (WT-2)

Agent response assessment: **correct**. Both dataset names match the references; the cited experiment windows identify them by the abbreviations PTB and WT-2.

### Claim 1

The authors used the Penn Treebank (PTB) dataset and the WikiText-2 (WT-2) dataset for training and evaluation.

Agent support: **partially_supported**. Use of PTB and WT-2 for experiments/training is explicit. Their expanded dataset names are not defined within these particular cited windows; a definition citation would make the attribution complete.

Human support: **pending**

Human note: 

<details><summary>Cited source passages</summary>

`1808.09029:s0007:p0001:c0000` — Set-up, characters 0:770

> We extend the language model, AWD-LSTM BIBREF0 , by replacing LSTM layers with PRU. Our model uses 3-layers of PRU with an embedding size of 400. The number of parameters learned by state-of-the-art methods vary from 18M to 66M with majority of the methods learning about 22M to 24M parameters on the PTB dataset. For a fair comparison with state-of-the-art methods, we fix the model size to 19M and vary the value of INLINEFORM0 and hidden layer sizes so that total number of learned parameters is similar across different configurations. We use 1000, 1200, and 1400 as hidden layer sizes for values of INLINEFORM1 =1,2, and 4, respectively. We use the same settings for the WT-2 dataset. We set the number of pyramidal levels INLINEFORM2 to two in our experiments and 

`1808.09029:s0007:p0001:c0001` — Set-up, characters 641:1039

> . We use the same settings for the WT-2 dataset. We set the number of pyramidal levels INLINEFORM2 to two in our experiments and use average pooling for sub-sampling. These values are selected based on our ablation experiments on the validation set (Section SECREF39 ). We measure the performance of our models in terms of word-level perplexity. We follow the same training strategy as in BIBREF0 .

</details>

## 26. Do the answered questions measure for the usefulness of the answer?

Question ID: `9af3142630b350c93875441e1e1767312df76d17`; paper: `1703.04001`.
Status: **insufficient_evidence**. Request: `6e09b914fbf448a08375202367ab3aa4`.

- [ ] Human reviewed

Human correctness: **pending**

Benchmark references (annotations can disagree):
- No

Agent response assessment: **refusal**. The supplied introduction explicitly defines answerability as whether a posted question eventually receives an answer. A qualified No distinguishing answer presence from usefulness is supported and matches the reference; blanket refusal is overly cautious.

<details><summary>Supplied passages for refusal/error inspection</summary>

`1703.04001:abstract:p0000:c0000` — Abstract, characters 0:858

> Quora is one of the most popular community Q&A sites of recent times. However, many question posts on this Q&A site often do not get answered. In this paper, we quantify various linguistic activities that discriminates an answered question from an unanswered one. Our central finding is that the way users use language while writing the question text can be a very effective means to characterize answerability. This characterization helps us to predict early if a question remaining unanswered for a specific time period t will eventually be answered or not and achieve an accuracy of 76.26% (t = 1 month) and 68.33% (t = 3 months). Notably, features representing the language use patterns of the users are most discriminative and alone account for an accuracy of 74.18%. We also compare our method with some of the similar works (Dror et al., Yang et al.) 

`1703.04001:s0000:p0000:c0001` — Introduction, characters 762:1722

> , Yahoo! Answers etc. and these are some of the prime reasons behind its popularity in recent times. Quality question posting and getting them answered are the key objectives of any Q&A site. In this study we focus on the answerability of questions on Quora, i.e., whether a posted question shall eventually get answered. In Quora, the questions with no answers are referred to as â€œopen questionsâ€‌. These open questions need to be studied separately to understand the reason behind their not being answered or to be precise, are there any characteristic differences between `open' questions and the answered ones. For example, the question â€œWhat are the most promising advances in the treatment of traumatic brain injuries?â€‌ was posted on Quora on 23rd June, 2011 and got its first answer after almost 2 years on 22nd April, 2013. The reason that this question remained open so long might be the hardness of answering it and the lack of visibility and experts 

`1703.04001:s0000:p0002:c0000` — Introduction, characters 0:616

> There are several research works done in Q&A focusing on content of posts. BIBREF0 exploit community feedback to identify high quality content on Yahoo! Answers. BIBREF1 use textual features to predict answer quality on Yahoo! Answers. BIBREF2 , investigate predictors of answer quality through a comparative, controlled field study of user responses. BIBREF3 study the problem of how long questions remain unanswered. BIBREF4 propose a prediction model on how many answers a question shall receive. BIBREF5 analyze and predict unanswered questions on Yahoo Answers. BIBREF6 study question quality in Yahoo! Answers.

`1703.04001:s0002:p0005:c0000` — Linguistic activities on Quora, characters 0:987

> Askers of open questions use more function words, impersonal pronouns, articles on an average whereas asker of answered questions use more personal pronouns, conjunctions and adverbs to describe their questions. Essentially, open questions lack content words compared to answered questions which, in turn, affects the readability of the question. As far as the psychological aspects are concerned, answered question askers tend to use more social, family, human related words on average compared to an open question asker. The open question askers express more positive emotions whereas the answered question asker tend to express more negative emotions in their texts. Also, answered question askers are more emotionally involved and their questions reveal higher usage of anger, sadness, anxiety related words compared to that of open questions. Open questions, on the other hand, contains more sexual, body, health related words which might be reasons why they do not attract answers.

`1703.04001:s0002:p0006:c0000` — Linguistic activities on Quora, characters 0:390

> In table 2 , we show a collection of examples of open questions to illustrate that many of the above quantities based on the linguistic activities described in this section naturally correspond to the factors that human judges consider responsible for a question remaining unanswered. This is one of the prime reasons why these quantities qualify as appropriate indicators of answerability.

</details>

## 27. What are the three regularization terms?

Question ID: `6becff2967fe7c5256fe0b00231765be5b9db9f1`; paper: `1503.00841`.
Status: **answered**. Request: `e3cd5d7d9ef14716bf18e2b0bb035ff5`.

- [ ] Human reviewed

Human correctness: **pending**

Benchmark references (annotations can disagree):
- a regularization term associated with neutral features, the maximum entropy of class distribution regularization term, the KL divergence between reference and predicted class distribution
- a regularization term associated with neutral features,  the maximum entropy of class distribution, KL divergence between reference and predicted class distribution

Agent response assessment: **correct**. All three regularization terms match the references and the explicitly enumerated source list.

### Claim 1

(1) a regularization term associated with neutral features

Agent support: **fully_supported**. Neutral-feature regularization is explicit in the source list.

Human support: **pending**

Human note: 

### Claim 2

(2) the maximum entropy of class distribution regularization term

Agent support: **fully_supported**. Maximum entropy of the class distribution is explicit in the source list.

Human support: **pending**

Human note: 

### Claim 3

(3) the KL divergence between reference and predicted class distribution

Agent support: **fully_supported**. KL divergence between reference and predicted class distributions is explicit in the source list.

Human support: **pending**

Human note: 

<details><summary>Cited source passages</summary>

`1503.00841:s0000:p0005:c0000` — Introduction, characters 0:570

> More specifically, we explore three regularization terms to address the problem: (1) a regularization term associated with neutral features; (2) the maximum entropy of class distribution regularization term; and (3) the KL divergence between reference and predicted class distribution. For the first manner, we simply use the most common features as neutral features and assume the neutral features are distributed uniformly over class labels. For the second and third one, we assume we have some knowledge about the class distribution which will be detailed soon later.

</details>

## 28. How do they obtain psychological dimensions of people?

Question ID: `07d15501a599bae7eb4a9ead63e9df3d55b3dc35`; paper: `1612.06685`.
Status: **error**. Request: `0c52b70754e743f1a482eb4fcc0987fb`.

- [ ] Human reviewed

Human correctness: **pending**

Benchmark references (annotations can disagree):
- using the Meaning Extraction Method
- Unanswerable

Agent response assessment: **service_error**. Generation failed draft validation with citation_not_supplied. The invalid response is not shown as an answer or reclassified as insufficient evidence. Known usage is retained; no validated claims exist to audit.

<details><summary>Supplied passages for refusal/error inspection</summary>

`1612.06685:abstract:p0000:c0000` — Abstract, characters 0:579

> People's personality and motivations are manifest in their everyday language usage. With the emergence of social media, ample examples of such usage are procurable. In this paper, we aim to analyze the vocabulary used by close to 200,000 Blogger users in the U.S. with the purpose of geographically portraying various demographic, linguistic, and psychological dimensions at the state level. We give a description of a web-based tool for viewing maps that depict various characteristics of the social media users as derived from this large blog dataset of over two billion words.

`1612.06685:s0004:p0000:c0000` — Linguistic Maps, characters 0:765

> Another use of the information found in our dataset is to build linguistic maps, which reflect the geographic lexical variation across the 50 states BIBREF7 . We generate maps that represent the relative frequency by which a word occurs in the different states. Figure FIGREF3 shows sample maps created for two different words. The figure shows the map generated for one location specific word, Maui, which unsurprisingly is found predominantly in Hawaii, and a map for a more common word, lake, which has a high occurrence rate in Minnesota (Land of 10,000 Lakes) and Utah (home of the Great Salt Lake). Our demo described in Section SECREF4 , can also be used to generate maps for function words, which can be very telling regarding people's personality BIBREF8 .

`1612.06685:s0007:p0000:c0000` — Conclusions, characters 0:609

> In this paper, we showed how we can effectively leverage a prodigious blog dataset. Not only does the dataset bring out the extensive linguistic content reflected in the blog posts, but also includes location information and rich metadata. These data allow for the generation of maps that reflect the demographics of the population, variations in language use, and differences in psycholinguistic and semantic categories. These mappings can be valuable to both psychologists and linguists, as well as lexicographers. A prototype demo has been made available together with the code used to collect our dataset.

`1612.06685:s0005:p0001:c0000` — Psycholinguistic and Semantic Maps, characters 0:836

> LIWC. In addition to individual words, we can also create maps for word categories that reflect a certain psycholinguistic or semantic property. Several lexical resources, such as Roget or Linguistic Inquiry and Word Count BIBREF9 , group words into categories. Examples of such categories are Money, which includes words such as remuneration, dollar, and payment; or Positive feelings with words such as happy, cheerful, and celebration. Using the distribution of the individual words in a category, we can compile distributions for the entire category, and therefore generate maps for these word categories. For instance, figure FIGREF8 shows the maps created for two categories: Positive Feelings and Money. The maps are not surprising, and interestingly they also reflect an inverse correlation between Money and Positive Feelings .

`1612.06685:s0000:p0001:c0000` — Introduction, characters 0:867

> For this paper, we compiled a very large geolocated collection of blogs, written by individuals located in the U.S., with the purpose of creating insightful mappings of the blogging community. In particular, during May-July 2015, we gathered the profile information for all the users that have self-reported their location in the U.S., along with a number of posts for all their associated blogs. We utilize this blog collection to generate maps of the U.S. that reflect user demographics, language use, and distributions of psycholinguistic and semantic word classes. We believe that these maps can provide valuable insights and partial verification of previous claims in support of research in linguistic geography BIBREF1 , regional personality BIBREF2 , and language analysis BIBREF3 , BIBREF4 , as well as psychology and its relation to human geography BIBREF5 .

</details>

## 29. Does the corpus contain only English documents?

Question ID: `8e44c02c2d9fa56fb74ace35ee70a5add50b52ae`; paper: `1704.04452`.
Status: **insufficient_evidence**. Request: `0abf908b14db412f9c2436e55acb0f4e`.

- [ ] Human reviewed

Human correctness: **pending**

Benchmark references (annotations can disagree):
- Yes
- Unanswerable
- Unanswerable

Agent response assessment: **refusal**. No supplied passage establishes that every corpus document is English. One reference says Yes and two say unanswerable; a refusal avoids inferring a universal language restriction from examples.

<details><summary>Supplied passages for refusal/error inspection</summary>

`1704.04452:s0015:p0001:c0000` — Concept Maps, characters 0:572

> To obtain a better picture of what kind of text spans have been used as labels, we automatically tagged them with their part-of-speech and determined their head with a dependency parser. Concept labels tend to be headed by nouns (82%) or verbs (15%), while they also contain adjectives, prepositions and determiners. Relation labels, on the other hand, are almost always headed by a verb (94%) and contain prepositions, nouns and particles in addition. These distributions are very similar to those reported by Villalon.2010 for their (single-document) concept map corpus.

`1704.04452:s0014:p0000:c0000` — Document Clusters, characters 0:717

> The corpus consists of document clusters for 30 different topics. Each of them contains around 40 documents with on average 2413 tokens, which leads to an average cluster size of 97,880 token. With these characteristics, the document clusters are 15 times larger than typical DUC clusters of ten documents and five times larger than the 25-document-clusters (Table TABREF26 ). In addition, the documents are also more variable in terms of length, as the (length-adjusted) standard deviation is twice as high as in the other corpora. With these properties, the corpus represents an interesting challenge towards real-world application scenarios, in which users typically have to deal with much more than ten documents.

`1704.04452:s0014:p0001:c0000` — Document Clusters, characters 0:454

> Because we used a large web crawl as the source for our corpus, it contains documents from a variety of genres. To further analyze this property, we categorized a sample of 50 documents from the corpus. Among them, we found professionally written articles and blog posts (28%), educational material for parents and kids (26%), personal blog posts (16%), forum discussions and comments (12%), commented link collections (12%) and scientific articles (6%).

`1704.04452:s0002:p0003:c0000` — Related Work, characters 0:299

> For concept map generation, one corpus with human-created summary concept maps for student essays has been created BIBREF28 . In contrast to our corpus, it only deals with single documents, requires a two orders of magnitude smaller amount of compression of the input and is not publicly available .

`1704.04452:s0000:p0002:c0000` — Introduction, characters 0:522

> The corresponding task that we propose is concept-map-based MDS, the summarization of a document cluster in the form of a concept map. In order to develop and evaluate methods for the task, gold-standard corpora are necessary, but no suitable corpus is available. The manual creation of such a dataset is very time-consuming, as the annotation includes many subtasks. In particular, an annotator would need to manually identify all concepts in the documents, while only a few of them will eventually end up in the summary.

</details>

## 30. How are the interpretability merits of the approach demonstrated?

Question ID: `67e9e147b2cab5ba43572ce8a17fc863690172f0`; paper: `1912.00667`.
Status: **answered**. Request: `9cbd25964d7044b6ad23ad702f465e08`.

- [ ] Human reviewed

Human correctness: **pending**

Benchmark references (annotations can disagree):
- By involving humans for post-hoc evaluation of model's interpretability
- directly solicits informative keywords from the crowd for model training, thereby providing human-understandable explanations for the improved model

Agent response assessment: **partially_correct**. The crowd-keyword training explanation matches the second reference and the source, unlike the first reference's post-hoc description. The extra assertion that expectations are explicitly communicated to users is not established by its citation.

### Claim 1

The approach demonstrates interpretability by directly soliciting informative keywords from the crowd for model training, thereby providing humanأ¢â‚¬â€کunderstandable explanations for the improved model.

Agent support: **fully_supported**. The cited related-work paragraph directly contrasts post-hoc evaluation with the proposed crowd-keyword approach and human-understandable explanations.

Human support: **pending**

Human note: 

### Claim 2

The model training process is made more transparent through the discovery of new keywords and their associated expectations, which are explicitly communicated to users.

Agent support: **partially_supported**. The abstract says discovered keywords and expectations make training more transparent, but does not state explicit communication to users.

Human support: **pending**

Human note: 

<details><summary>Cited source passages</summary>

`1912.00667:s0012:p0001:c0001` — Related Work, characters 720:1040

> BIBREF11, BIBREF35, BIBREF12, for which humans are increasingly involved, for instance for post-hoc evaluations of the model's interpretability. In contrast, our approach directly solicits informative keywords from the crowd for model training, thereby providing human-understandable explanations for the improved model.

`1912.00667:abstract:p0000:c0001` — Abstract, characters 883:1312

> the model in order to discover new keywords that are most beneficial for model training. These keywords and their expectation not only improve the resulting performance but also make the model training process more transparent. We empirically demonstrate the merits of our approach, both in terms of accuracy and interpretability, on multiple real-world datasets and show that our approach improves the state of the art by 24.3%.

</details>

