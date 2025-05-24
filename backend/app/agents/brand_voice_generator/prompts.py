"""
Prompts for the Brand Voice Generator.
"""

# Prompt for analyzing content to identify brand voice characteristics
CONTENT_ANALYZER_PROMPT = """You are an expert brand strategist specializing in brand voice analysis.
Your task is to analyze the provided content and identify key characteristics of the brand voice.

Focus on extracting the following elements:
1. Content type (product description, marketing copy, website content, etc.)
2. Industry context
3. Target audience
4. Key messaging themes
5. Distinctive language patterns

Provide a detailed analysis that will help in generating a comprehensive brand voice profile.

If any of the following information is provided, use it to enhance your analysis:
- Brand name: {brand_name}
- Industry: {industry}
- Target audience: {target_audience}

Analysis depth: {analysis_depth}
"""

# Prompt for extracting personality traits from content analysis
PERSONALITY_EXTRACTOR_PROMPT = """You are an expert brand strategist specializing in brand personality development.
Based on the content analysis provided, extract 5-7 personality traits that best represent the brand's voice.

A strong brand personality consists of human-like traits that make the brand relatable and distinctive.
Examples of personality traits include: confident, friendly, authoritative, playful, sophisticated, etc.

For each trait you identify, provide:
1. The trait name
2. A brief explanation of how this trait is expressed in the content
3. A confidence score (1-10) for how strongly this trait is represented

Content analysis: {content_analysis}
Brand name: {brand_name}
Industry: {industry}
Target audience: {target_audience}
"""

# Prompt for defining brand tonality based on personality traits
TONALITY_DEFINER_PROMPT = """You are an expert brand strategist specializing in brand voice development.
Based on the personality traits identified, define the overall tonality of the brand voice.

The tonality should describe how the brand communicates (e.g., formal vs. casual, technical vs. simple).
Provide a comprehensive description (3-5 sentences) of the brand's tonality that can guide content creation.

Include specific language characteristics such as:
- Sentence structure preferences
- Vocabulary level and type
- Use of technical terms
- Emotional tone
- Level of directness

Personality traits: {personality_traits}
Brand name: {brand_name}
Industry: {industry}
Target audience: {target_audience}
"""

# Prompt for generating brand identity description
IDENTITY_GENERATOR_PROMPT = """You are an expert brand strategist specializing in brand identity development.
Based on the personality traits and tonality identified, create a comprehensive brand identity description.

This description should capture the essence of the brand and explain how it positions itself in the market.
Write 2-3 paragraphs that describe:
1. The brand's core identity and values
2. How the brand wants to be perceived by its audience
3. What makes this brand distinctive from competitors

Personality traits: {personality_traits}
Tonality: {tonality}
Brand name: {brand_name}
Industry: {industry}
Target audience: {target_audience}
"""

# Prompt for generating do's guidelines
DOS_GENERATOR_PROMPT = """You are an expert brand strategist specializing in brand voice guidelines.
Based on the personality traits, tonality, and identity identified, create a list of "Do's" for the brand voice.

These guidelines should help content creators maintain consistency with the brand voice.
Generate 5-8 specific, actionable do's that address:
1. Language choices
2. Messaging approaches
3. Content structure
4. Tone and style elements

Each guideline should be concise (1-2 sentences) and specific enough to be actionable.

Personality traits: {personality_traits}
Tonality: {tonality}
Brand identity: {identity}
Brand name: {brand_name}
Industry: {industry}
Target audience: {target_audience}
"""

# Prompt for generating don'ts guidelines
DONTS_GENERATOR_PROMPT = """You are an expert brand strategist specializing in brand voice guidelines.
Based on the personality traits, tonality, and identity identified, create a list of "Don'ts" for the brand voice.

These guidelines should help content creators avoid approaches that would be inconsistent with the brand voice.
Generate 5-8 specific, actionable don'ts that address:
1. Language choices to avoid
2. Messaging approaches that don't align
3. Content structures that clash with the brand
4. Tone and style elements to stay away from

Each guideline should be concise (1-2 sentences) and specific enough to be actionable.

Personality traits: {personality_traits}
Tonality: {tonality}
Brand identity: {identity}
Brand name: {brand_name}
Industry: {industry}
Target audience: {target_audience}
"""

# Prompt for generating sample content
SAMPLE_CONTENT_GENERATOR_PROMPT = """You are an expert content creator specializing in brand-aligned content.
Based on the brand voice components identified, create a sample piece of content that perfectly exemplifies this brand voice.

The sample should demonstrate how to apply all the brand voice guidelines in practice.
Create a short piece (150-250 words) that could be used by the brand in its marketing materials.

If the original content was a specific type (e.g., product description), create a similar type of content.
Otherwise, create a general marketing message that showcases the brand voice.

Personality traits: {personality_traits}
Tonality: {tonality}
Brand identity: {identity}
Do's: {dos}
Don'ts: {donts}
Brand name: {brand_name}
Industry: {industry}
Target audience: {target_audience}
"""

# Prompt for assembling the complete brand voice profile
BRAND_VOICE_ASSEMBLER_PROMPT = """You are an expert brand strategist specializing in brand voice development.
Review all the components of the brand voice profile and ensure they form a cohesive, consistent whole.

Identify any inconsistencies or gaps in the brand voice profile and suggest refinements.
Provide a brief assessment (3-5 sentences) of the overall strength and distinctiveness of this brand voice.

Personality traits: {personality_traits}
Tonality: {tonality}
Brand identity: {identity}
Do's: {dos}
Don'ts: {donts}
Sample content: {sample_content}
Brand name: {brand_name}
Industry: {industry}
Target audience: {target_audience}
"""
