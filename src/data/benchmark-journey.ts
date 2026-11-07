import final4x4 from './futoshiki-final-4x4.json';

export interface JourneyBenchmark {
  label: string;
  passAt1: number | null;
  passAt8: number | null;
  protocol: string;
}

export interface JourneyChapter {
  id: string;
  shortTitle: string;
  title: string;
  model: string;
  note: string;
  benchmarks: JourneyBenchmark[];
  source?: { label: string; href: string };
}

const unknown = (label: string, protocol: string): JourneyBenchmark => ({ label, passAt1: null, passAt8: null, protocol });

// Fractions, not rounded percentages. Null means no verified measurement for
// this exact checkpoint and panel; it must never be rendered as zero.
export const journeyChapters: JourneyChapter[] = [
  {
    id: 'instruct', shortTitle: 'Starting point', title: 'Before the climb',
    model: 'LFM2.5-1.2B-Instruct',
    note: 'The pretrained, instruction-tuned starting model. Future tasks are on the horizon.',
    benchmarks: [
      unknown('Futoshiki 4×4', 'No verified puzzle baseline is attached to the untouched Instruct checkpoint yet.'),
      unknown('Futoshiki 5×5', 'No verified puzzle baseline is attached to the untouched Instruct checkpoint yet.'),
    ],
    source: { label: 'Starting model card', href: 'https://huggingface.co/LiquidAI/LFM2.5-1.2B-Instruct' },
  },
  {
    id: 'post-countdown', shortTitle: 'Arithmetic', title: 'A foothold in arithmetic',
    model: 'Post-GSM8K and Countdown checkpoint',
    note: 'The first recorded puzzle scores in this lineage come after arithmetic training.',
    benchmarks: [
      { label: 'Futoshiki 4×4', passAt1: 1 / 1024, passAt8: 1 / 128, protocol: '128 puzzles × 8 attempts; 4,096-token cap. One correct completion.' },
      { label: 'Futoshiki 5×5', passAt1: 0, passAt8: 0, protocol: '32 puzzles × 8 attempts; 4,096-token protocol in the historical panel.' },
    ],
    source: { label: 'Archived lineage results', href: 'https://wandb.ai/lukas928/simple-pt/runs/01m6d5a7' },
  },
  {
    id: 'projection', shortTitle: 'First foothold', title: '256 demonstrations',
    model: 'Solver projection SFT · one epoch',
    note: 'A small set of verified examples provides another starting point for RL.',
    benchmarks: [
      { label: 'Futoshiki 4×4', passAt1: 0.0419921875, passAt8: 0.21875, protocol: '128 puzzles × 8 attempts; 4,096-token cap.' },
      unknown('Futoshiki 5×5', 'No score for this panel was reported for the selected SFT checkpoint.'),
    ],
    source: { label: 'Projection SFT run', href: 'https://wandb.ai/lukas928/simple-pt/runs/lu8nhv18' },
  },
  {
    id: 'rl750', shortTitle: '4×4 practice', title: '750 RL updates',
    model: '4×4 FlashREINFORCE · update 750',
    note: 'These puzzle scores use an 8K evaluation window, including the earlier checkpoint.',
    benchmarks: [
      { label: 'Futoshiki 4×4', passAt1: 0.5712890625, passAt8: 0.8984375, protocol: '128 puzzles × 8 attempts; 8,192-token cap.' },
      { label: 'Futoshiki 5×5', passAt1: 0.01953125, passAt8: 0.0625, protocol: '32 puzzles × 8 attempts; 8,192-token cap.' },
    ],
    source: { label: 'Matched 8K evaluation', href: 'https://wandb.ai/lukas928/simple-pt/runs/01m6d5a7' },
  },
  {
    id: 'rl1000', shortTitle: '4×4 climb', title: '1,000 RL updates',
    model: '4×4 FlashREINFORCE · update 1,000',
    note: 'Strong performance on 4×4 leaves a substantial gap at the larger puzzle size.',
    benchmarks: [
      { label: 'Futoshiki 4×4', passAt1: 793 / 1024, passAt8: 119 / 128, protocol: '128 puzzles × 8 attempts; 8,192-token cap.' },
      { label: 'Futoshiki 5×5', passAt1: 13 / 256, passAt8: 5 / 32, protocol: '32 puzzles × 8 attempts; 8,192-token cap.' },
    ],
    source: { label: 'Final 4×4 evaluation', href: 'https://wandb.ai/lukas928/simple-pt/runs/01m6d5a7' },
  },
  {
    id: 'curriculum', shortTitle: '5×5 arc', title: 'A restart and a harder curriculum',
    model: 'Post-projection 5×5 curriculum · final update 300',
    note: 'After the 5×5 curriculum, this checkpoint also improved on the earlier 4×4 test.',
    benchmarks: [
      { label: 'Futoshiki 4×4', passAt1: final4x4.pass_at_1, passAt8: final4x4.pass_at_8, protocol: `128 puzzles × 8 attempts; 8,192-token cap, temperature 1. ${final4x4.correct_completions}/${final4x4.samples} correct attempts; ${final4x4.solved_puzzles}/${final4x4.puzzles} puzzles solved. Evaluated November 6 after the 5×5 curriculum, on the same 4×4 test panel used at update 1,000.` },
      { label: 'Futoshiki 5×5', passAt1: 377 / 1024, passAt8: 0.671875, protocol: '128 mixed-tier puzzles × 8 attempts; 8,192-token cap. A different panel from the early 5×5 test.' },
    ],
    source: { label: 'Final 5×5 curriculum run', href: 'https://wandb.ai/lukas928/simple-pt/runs/uuwdywyl' },
  },
];

export function formatJourneyScore(value: number | null) {
  return value === null ? '—' : `${(value * 100).toFixed(2)}%`;
}
