#include <stdint.h>
#include <stdio.h>

typedef struct { int k, lam, sum; } Case;

static int corr(const int s[9], int shift) {
    int total = 0;
    for (int j = 0; j < 9; ++j) total += s[j] * s[(j - shift + 9) % 9];
    return total;
}

int main(void) {
    const Case cases[] = {
        {10,1,6}, {14,5,12}, {17,4,11}, {22,3,10}, {22,9,16}, {25,16,21}
    };
    const uint64_t domain = 40353607ULL; /* 7^9 */
    for (unsigned ci = 0; ci < sizeof(cases)/sizeof(cases[0]); ++ci) {
        uint64_t survivors = 0, principal_candidates = 0, square_candidates = 0;
        int first[9] = {0};
        const int n = cases[ci].k - cases[ci].lam;
        for (uint64_t code = 0; code < domain; ++code) {
            uint64_t q = code;
            int s[9], sum = 0, c0 = 0;
            for (int j = 0; j < 9; ++j) {
                s[j] = (int)(q % 7) - 3;
                q /= 7;
                sum += s[j];
                c0 += s[j] * s[j];
            }
            if (sum != cases[ci].sum) continue;
            ++principal_candidates;
            const int A = c0 - n;
            const int bnum = sum * sum - n - 3 * A;
            if (bnum % 6) continue;
            const int B = bnum / 6;
            if (corr(s,3) != A) continue;
            ++square_candidates;
            if (corr(s,1) != B || corr(s,2) != B || corr(s,4) != B) continue;
            if (!survivors) for (int j = 0; j < 9; ++j) first[j] = s[j];
            ++survivors;
        }
        printf("(27,%d,%d) domain=%llu principal=%llu prefinal=%llu survivors=%llu first=[",
            cases[ci].k, cases[ci].lam,
            (unsigned long long)domain,
            (unsigned long long)principal_candidates,
            (unsigned long long)square_candidates,
            (unsigned long long)survivors);
        for (int j = 0; j < 9; ++j) printf("%s%d", j ? "," : "", first[j]);
        printf("]\n");
    }
    return 0;
}
